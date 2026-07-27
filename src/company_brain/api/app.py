"""FastAPI app backing the web UI.

The principal comes from the `X-Principal` header, never from a request body.
That is a **demo stand-in** for a session cookie or bearer token — in M1 the UI
lets you switch principals freely, which is the point of the demo. What matters
architecturally is the shape: identity arrives out-of-band, is resolved once per
request, and every handler below receives an already-constructed AccessFilter.
No handler reads an identity out of user-supplied JSON.

The UI never filters by permission (invariant 17). Everything here returns
ACL-projected data, so if the client is doing access control, this file has a bug.
"""

from __future__ import annotations

import asyncio
from collections import Counter
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from company_brain.acl.grants import AccessFilter
from company_brain.app import PRINCIPALS, STORE_ROOT, App, build_app
from company_brain.audit.log import Action, AuditLog, Outcome, Surface, summarize
from company_brain.collab.guard import FenceViolation
from company_brain.collab.hub import CollabHub
from company_brain.collab.session import SessionRegistry, participant_color
from company_brain.gmail_triage.oauth import router as gmail_oauth_router
from company_brain.gmail_triage.routes import router as gmail_routes_router
from company_brain.index.base import IndexedNode
from company_brain.outreach.apollo import ApolloError, choose_lead_source
from company_brain.outreach.drafts import (
    MAX_FACTS,
    OutreachDraft,
    OutreachError,
    OutreachState,
    OutreachStore,
    compose,
    draft_id,
)
from company_brain.retrieve.hybrid import HybridRetriever
from company_brain.schemas.acl import Principal, Sensitivity
from company_brain.schemas.edges import Edge, EdgeStatus
from company_brain.schemas.nodes import NodeStatus, NodeType
from company_brain.store.repository import NodeNotFoundError
from company_brain.synthesize.answer import (
    CitationLeakError,
    UncitedAnswerError,
    validate,
)

api = FastAPI(title="company_brain", version="0.1.0")

# The UI is served from a different origin in dev (Vite on 5173).
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def _app(store: str = str(STORE_ROOT)) -> App:
    """Build once and reuse. The index is rebuilt from markdown at startup;
    for M1 that is fast enough to do eagerly and simpler than invalidation."""
    instance = build_app(Path(store))
    instance.load_index()
    return instance


# Set when a review decision changes the graph. The index is disposable
# (invariant 2), so the fix is always "rebuild it from markdown" — the only
# question is when. Rebuilding inside the decision handler put a full reindex of
# every node on the reviewer's critical path, fifty times over, which is a
# meaningful share of the fifteen-minute budget the ROADMAP allows for the whole
# queue. So the decision marks the index stale and returns, and the next request
# that actually needs retrieval pays for one rebuild covering all of them.
_index_stale = False

# Source-artifact modification times, node id -> RFC-3339. Read from the store
# rather than from the index because invariant 4 keeps every timestamp in the
# markdown and out of everything derived from it — the index has no idea when a
# document was last touched upstream, and giving it one would be inventing a
# field. Parsing the tree is cheap on this corpus but it is still per-request
# work with no reason to be, so it is cached beside the index and dropped with it.
#
# Held against the App that produced it rather than as a bare dict: a test that
# overrides `get_app` to point at a temp store must not be served another
# store's timestamps, and identity is the one key that cannot get that wrong.
_modified: tuple[App, dict[str, str]] | None = None


def mark_index_stale() -> None:
    global _index_stale, _modified
    _index_stale = True
    _modified = None


def _modified_times(instance: App) -> dict[str, str]:
    global _modified
    if _modified is None or _modified[0] is not instance:
        found: dict[str, str] = {}
        for node in instance.repo.walk():
            stamps = node.frontmatter.timestamps
            when = stamps.modified or stamps.created
            if when is not None:
                found[node.id] = when.isoformat()
        _modified = (instance, found)
    return _modified[1]


def get_app() -> App:
    """The app, with a fresh index if a decision invalidated it.

    Review and audit routes never call this path's rebuild — they read the store
    directly — so clearing a queue costs no reindexing at all until the reviewer
    asks a question again.
    """
    global _index_stale
    instance = _app()
    if _index_stale:
        instance.load_index()
        _index_stale = False
    return instance


def get_access(
    instance: Annotated[App, Depends(get_app)],
    x_principal: Annotated[str, Header()] = "ceo",
) -> AccessFilter:
    if x_principal not in PRINCIPALS:
        raise HTTPException(400, f"unknown principal {x_principal!r}")
    return instance.access(PRINCIPALS[x_principal])


def get_reviewer(x_principal: Annotated[str, Header()] = "ceo") -> Principal:
    """Who is deciding. Out-of-band, exactly like every other identity here.

    A review decision is a graph write, so it needs a name on it — and the name
    comes from the header, never from the request body carrying the decision.
    """
    if x_principal not in PRINCIPALS:
        raise HTTPException(400, f"unknown principal {x_principal!r}")
    return PRINCIPALS[x_principal]


def get_audit(instance: Annotated[App, Depends(get_app)]) -> AuditLog:
    return instance.audit(Surface.API)


# ---- models ------------------------------------------------------------


class PrincipalOut(BaseModel):
    id: str
    display: str
    visible_sources: int


class AskIn(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=6, ge=1, le=20)


class CitationOut(BaseModel):
    node_id: str
    title: str
    snippet: str


class AskOut(BaseModel):
    question: str
    text: str
    citations: list[CitationOut]
    asserted: list[str]
    inferred: list[str]
    insufficient_evidence: bool
    seed_count: int
    expanded_count: int
    withheld_by_acl: int
    refused: str | None = None


class NodeSummary(BaseModel):
    id: str
    type: str
    title: str


class EdgeOut(BaseModel):
    predicate: str
    # None means "this node" — the document itself is the subject, which is the
    # normal case for mentions/authored_by. Present for third-party relations,
    # where omitting it renders "owns processes/x" with no owner shown.
    subject: str | None
    subject_title: str | None
    object: str
    object_title: str
    confidence: float
    provenance: str
    status: str


class NodeDetail(BaseModel):
    id: str
    type: str
    title: str
    body: str
    sensitivity: str
    relations: list[EdgeOut]


class OverviewSource(BaseModel):
    """One ACL ref this principal holds, and how much of the store sits under it."""

    ref: str
    ceiling: str
    nodes: int


class OverviewNode(BaseModel):
    id: str
    type: str
    title: str
    sensitivity: str
    # Visible degree — see `overview` for why it is not the stored degree.
    degree: int = 0
    modified: str | None = None


class OverviewOut(BaseModel):
    """The graph as it looks from where this principal is standing.

    Two of these counts describe things the caller cannot open —
    ``withheld_nodes`` and ``withheld_sources``. That is a deliberate
    disclosure and not a slip. It is already established in both directions:
    ``/api/principals`` publishes every principal's visible-source count to
    every caller, and every ``/api/ask`` response carries ``withheld_by_acl``.
    The *names* stay out, which is the part that would be new — only the
    magnitude is reported, because a contractor who sees eleven nodes and no
    other signal will read eleven nodes as the whole company.
    """

    nodes: int
    edges: int
    by_type: dict[str, int]
    sources: list[OverviewSource]
    withheld_nodes: int
    withheld_sources: int
    connected: list[OverviewNode]
    recent: list[OverviewNode]


class RelationDiffOut(BaseModel):
    """One edge, as a line in a diff rather than as a fact."""

    predicate: str
    subject: str | None
    subject_title: str | None
    object: str
    object_title: str | None
    confidence: float
    provenance: str
    quote: str


class DiffLineOut(BaseModel):
    # context | added | removed | gap
    kind: str
    text: str


class LeadOut(BaseModel):
    """The contact Apollo resolved, or as much of one as it had.

    ``source`` is carried to the reviewer rather than dropped: "Apollo holds
    this address" and "we have a name and nothing else" are different claims,
    and approving a message to a contact nobody verified is the mistake this
    field exists to prevent.
    """

    name: str
    email: str | None
    title: str | None
    organization: str | None
    linkedin_url: str | None
    source: str


class OutreachOut(BaseModel):
    draft_id: str
    node_id: str
    node_title: str
    sensitivity: str
    drafted_by: str
    created_at: str
    subject: str
    body: str
    # The graph statements the body was built from. The reviewer's equivalent
    # of edge evidence: check the source, not the prose.
    facts: list[str]
    lead: LeadOut | None
    lead_source: str
    state: str
    decided_by: str | None = None
    sent_by: str | None = None
    sent_at: str | None = None


class OutreachDraftIn(BaseModel):
    node_id: str = Field(min_length=1, max_length=400)


class OutreachSendIn(BaseModel):
    draft_id: str = Field(min_length=1, max_length=200)


class PendingOut(BaseModel):
    """One queue item, whatever produced it.

    Extraction-proposed edges and agent proposals are rendered through the same
    shape on purpose: to a reviewer they are the same job, and a UI with two
    layouts for one decision is a UI that costs twice as much to work through.
    An extraction-proposed edge *is* a diff — one added relation — so it is
    reported as one.
    """

    key: str
    # "edge" — from extraction; "proposal" — from an agent; "outreach" — a
    # message drafted for a real person, which is why it carries a body rather
    # than a relation diff.
    kind: str
    node_id: str
    node_title: str
    predicate: str | None
    subject: str | None
    subject_title: str | None
    object: str | None
    confidence: float | None
    quote: str
    summary: str
    # Present only for agent proposals: who proposed it, and for which human.
    # A suggestion nobody can attribute is a suggestion nobody should accept.
    proposed_by: str | None = None
    delegated_by: str | None = None
    # The target moved after the proposal was made; accepting would revert it.
    stale: bool = False
    body_diff: list[DiffLineOut] = []
    added_relations: list[RelationDiffOut] = []
    removed_relations: list[RelationDiffOut] = []
    # Outreach only: the message itself, so the reviewer reads what would go
    # out rather than a summary of it.
    outreach: OutreachOut | None = None


class ReviewStatsOut(BaseModel):
    pending: int
    pending_proposals: int
    pending_outreach: int
    by_predicate: dict[str, int]
    accept_rate: dict[str, list[int]]
    proposal_accept_rate: dict[str, list[int]]
    outreach_accept_rate: dict[str, list[int]]


class DecideItem(BaseModel):
    """One thing being decided, tagged with what it is.

    ``kind`` is the same discriminator the queue handed the client, validated
    back on the way in — so the server never infers a code path from the shape
    of a key, and a client cannot reach the proposal path by crafting a string
    that happens to look like a proposal id.
    """

    key: str = Field(min_length=1, max_length=400)
    kind: Literal["edge", "proposal", "outreach"]


class DecideIn(BaseModel):
    """A decision over one or many items, in the order the reviewer worked them.

    One list rather than one per kind: a mixed batch is the normal case, and
    splitting it at the wire would throw away the reviewer's ordering for no
    gain. Edges are still grouped by node before they are written — that
    batching is a store concern, decided here rather than asked of the caller.
    """

    items: list[DecideItem] = Field(default_factory=list, max_length=500)
    decision: str


class AuditOut(BaseModel):
    at: str
    surface: str
    actor: str
    delegated_by: str | None
    action: str
    outcome: str
    node_ids: list[str]
    proposal_id: str | None
    detail: str


# ---- routes ------------------------------------------------------------


@api.get("/api/health")
def health(instance: Annotated[App, Depends(get_app)]) -> dict[str, Any]:
    return {
        "ok": True,
        "providers": instance.providers.reason,
        "offline": instance.providers.offline,
        **instance.index.stats(),
    }


@api.get("/api/principals", response_model=list[PrincipalOut])
def principals(instance: Annotated[App, Depends(get_app)]) -> list[PrincipalOut]:
    """Drives the principal switcher, which is load-bearing rather than
    decorative: it is how the permission model is demonstrated."""
    return [
        PrincipalOut(
            id=p.id,
            display=p.display,
            visible_sources=len(instance.access(p).refs),
        )
        for p in PRINCIPALS.values()
    ]


class CitationLeakBlocked(RuntimeError):
    """A synthesized answer cited a node the principal cannot read."""


def answer_for(instance: App, access: AccessFilter, question: str, limit: int) -> AskOut:
    """Retrieve, synthesize, validate — the one path that produces an answer.

    Both the REST route and the shared ask room call this. Duplicating it would
    mean two citation validators, and the second one is always the one that
    rots: invariant 11 has to hold on every surface, not the one we remembered.
    """
    retrieval = HybridRetriever(instance.index, access).retrieve(question, limit=limit)
    answer = instance.providers.synthesizer().synthesize(question, retrieval, instance.index)

    refused: str | None = None
    try:
        validate(answer, retrieval, access, instance.index)
    except CitationLeakError as exc:
        # Never return the offending text. A leak is surfaced as a refusal.
        raise CitationLeakBlocked(str(exc)) from exc
    except UncitedAnswerError as exc:
        # Invariant 11: an uncited answer is an error, not a degraded response.
        # The UI renders this as a designed error state, not as prose.
        refused = str(exc)
        answer.text = ""
        answer.citations = []

    return AskOut(
        question=question,
        text=answer.text,
        citations=[
            CitationOut(node_id=c.node_id, title=c.title, snippet=c.snippet)
            for c in answer.citations
        ],
        asserted=answer.asserted,
        inferred=answer.inferred,
        insufficient_evidence=answer.insufficient_evidence,
        seed_count=retrieval.seed_count,
        expanded_count=retrieval.expanded_count,
        withheld_by_acl=retrieval.filtered_out,
        refused=refused,
    )


@api.post("/api/ask", response_model=AskOut)
def ask(
    body: AskIn,
    instance: Annotated[App, Depends(get_app)],
    access: Annotated[AccessFilter, Depends(get_access)],
) -> AskOut:
    try:
        return answer_for(instance, access, body.question, body.limit)
    except CitationLeakBlocked as exc:
        raise HTTPException(500, f"citation leak blocked: {exc}") from exc


@api.get("/api/nodes", response_model=list[NodeSummary])
def list_nodes(
    instance: Annotated[App, Depends(get_app)],
    access: Annotated[AccessFilter, Depends(get_access)],
    type: str | None = None,
    q: str | None = None,
    limit: int = 200,
) -> list[NodeSummary]:
    out: list[NodeSummary] = []
    for node_id in instance.repo.walk_ids(type):
        indexed = instance.index.get_node(node_id)
        if indexed is None or not access.allows(indexed.acl_ref, indexed.sensitivity):
            continue
        if q and q.lower() not in indexed.title.lower():
            continue
        out.append(NodeSummary(id=indexed.id, type=indexed.type, title=indexed.title))
        if len(out) >= limit:
            break
    return out


OVERVIEW_LIMIT = 8


def _overview_node(node: IndexedNode, degree: int, modified: str | None = None) -> OverviewNode:
    return OverviewNode(
        id=node.id,
        type=node.type,
        title=node.title,
        sensitivity=str(node.sensitivity),
        degree=degree,
        modified=modified,
    )


@api.get("/api/overview", response_model=OverviewOut)
def overview(
    instance: Annotated[App, Depends(get_app)],
    access: Annotated[AccessFilter, Depends(get_access)],
) -> OverviewOut:
    """What the graph contains, before anyone has asked it anything.

    The Ask surface opens on this rather than on an empty page: the useful
    first question depends on what is in there, and a principal cannot form one
    against a blank box. Every field is projected through `access` here, so the
    client renders what it is given and holds no filtering logic (invariant 17).
    """
    visible: dict[str, IndexedNode] = {}
    total = 0
    store_refs: set[str] = set()

    for node_id in instance.repo.walk_ids():
        indexed = instance.index.get_node(node_id)
        # Tombstones stay resolvable so old citations still land somewhere, but
        # they are not part of what the graph currently knows.
        if indexed is None or indexed.status != str(NodeStatus.ACTIVE):
            continue
        total += 1
        store_refs.add(indexed.acl_ref)
        if access.allows(indexed.acl_ref, indexed.sensitivity):
            visible[node_id] = indexed

    # Degree over edges with *both* endpoints visible. An edge into something
    # the principal cannot open is not a connection they have, and ranking on
    # it would let the ordering here describe the shape of the half of the
    # graph they were refused.
    degree: Counter[str] = Counter()
    edges = 0
    for indexed in visible.values():
        for edge in indexed.edges:
            if edge.status is not EdgeStatus.ACCEPTED:
                continue
            subject = edge.resolve_subject(indexed.id)
            if subject not in visible or edge.object not in visible:
                continue
            edges += 1
            degree[subject] += 1
            degree[edge.object] += 1

    per_ref: Counter[str] = Counter(n.acl_ref for n in visible.values())
    sources = sorted(
        (
            OverviewSource(ref=ref, ceiling=str(access.ceiling(ref) or ""), nodes=count)
            for ref, count in per_ref.items()
        ),
        key=lambda s: (-s.nodes, s.ref),
    )

    # Entities only. Documents are the bulk of the corpus and would fill the
    # list with the artifacts a fact came from rather than the fact's subject —
    # "who and what this company is made of" is the question being answered.
    entities = [n for n in visible.values() if n.type != str(NodeType.DOCUMENT)]
    connected = sorted(entities, key=lambda n: (-degree[n.id], n.id))[:OVERVIEW_LIMIT]

    stamps = _modified_times(instance)
    dated = sorted(
        ((stamps[n.id], n) for n in visible.values() if n.id in stamps),
        key=lambda pair: (pair[0], pair[1].id),
        reverse=True,
    )

    return OverviewOut(
        nodes=len(visible),
        edges=edges,
        by_type=dict(sorted(Counter(n.type for n in visible.values()).items())),
        sources=sources,
        withheld_nodes=total - len(visible),
        withheld_sources=len(store_refs - access.refs),
        connected=[_overview_node(n, degree[n.id]) for n in connected],
        recent=[
            _overview_node(n, degree[n.id], modified=when) for when, n in dated[:OVERVIEW_LIMIT]
        ],
    )


@api.get("/api/nodes/{node_id:path}", response_model=NodeDetail)
def get_node(
    node_id: str,
    instance: Annotated[App, Depends(get_app)],
    access: Annotated[AccessFilter, Depends(get_access)],
) -> NodeDetail:
    indexed = instance.index.get_node(node_id)
    # A node with no visible edges is a 404, not an empty page: an empty page
    # confirms the node exists (§6.3).
    if indexed is None or not access.allows(indexed.acl_ref, indexed.sensitivity):
        raise HTTPException(404, "not found")

    node = instance.repo.find(node_id)
    relations: list[EdgeOut] = []
    for edge in indexed.edges:
        target = instance.index.get_node(edge.object)
        if target is None or not access.allows(target.acl_ref, target.sensitivity):
            continue
        subject_node = instance.index.get_node(edge.subject) if edge.subject else None
        relations.append(
            EdgeOut(
                predicate=str(edge.predicate),
                subject=edge.subject,
                subject_title=subject_node.title if subject_node else None,
                object=edge.object,
                object_title=target.title,
                confidence=edge.confidence,
                provenance=str(edge.provenance),
                status=str(edge.status),
            )
        )
    relations.sort(key=lambda e: (e.status != str(EdgeStatus.ACCEPTED), e.predicate))

    return NodeDetail(
        id=indexed.id,
        type=indexed.type,
        title=indexed.title,
        body=node.body if node else "",
        sensitivity=str(indexed.sensitivity),
        relations=relations,
    )


def _title(instance: App, node_id: str | None) -> str | None:
    if not node_id:
        return None
    indexed = instance.index.get_node(node_id)
    return indexed.title if indexed else None


def _relation_out(instance: App, edge: Edge) -> RelationDiffOut:
    return RelationDiffOut(
        predicate=str(edge.predicate),
        subject=edge.subject,
        subject_title=_title(instance, edge.subject),
        object=edge.object,
        object_title=_title(instance, edge.object),
        confidence=edge.confidence,
        provenance=str(edge.provenance),
        quote=next((e.quote for e in edge.evidence if e.quote), "") or "",
    )


def _outreach_out(draft: OutreachDraft) -> OutreachOut:
    return OutreachOut(
        draft_id=draft.draft_id,
        node_id=draft.node_id,
        node_title=draft.node_title,
        sensitivity=str(draft.sensitivity),
        drafted_by=draft.drafted_by,
        created_at=draft.created_at.isoformat(),
        subject=draft.subject,
        body=draft.body,
        facts=list(draft.facts),
        lead=LeadOut(**draft.lead.to_dict()) if draft.lead else None,
        lead_source=draft.lead_source,
        state=str(draft.state),
        decided_by=draft.decided_by,
        sent_by=draft.sent_by,
        sent_at=draft.sent_at.isoformat() if draft.sent_at else None,
    )


def _decide_outreach(
    store: OutreachStore,
    draft_id: str,
    decision: Any,
    reviewer: Principal,
    audit: AuditLog,
) -> None:
    """Approve, reject, or reopen one draft, under the reviewer's identity.

    Approving does **not** send. It moves the draft to `approved`, which is the
    only state `/api/outreach/send` will accept — so the reviewer's accept and
    the decision to contact someone stay two separate acts with two separate
    records.
    """
    from company_brain.review.queue import Decision

    if decision is Decision.PENDING:
        store.reopen(draft_id, reviewer=reviewer.id)
        return
    state = OutreachState.APPROVED if decision is Decision.ACCEPTED else OutreachState.REJECTED
    draft = store.decide(draft_id, state, reviewer=reviewer.id)
    audit.record(
        actor=reviewer,
        action=Action.REVIEW_ACCEPT if decision is Decision.ACCEPTED else Action.REVIEW_REJECT,
        outcome=Outcome.OK,
        node_ids=[draft.node_id],
        detail=f"outreach {state}",
    )


@api.post("/api/outreach/draft", response_model=OutreachOut)
def outreach_draft(
    body: OutreachDraftIn,
    instance: Annotated[App, Depends(get_app)],
    access: Annotated[AccessFilter, Depends(get_access)],
    principal: Annotated[Principal, Depends(get_reviewer)],
    audit: Annotated[AuditLog, Depends(get_audit)],
) -> OutreachOut:
    """Draft a message from what the graph knows about a person. Never sends.

    Three refusals, in order, and the order matters:

    1. **Invisible node → 404.** Identical to `get_node`, and for the same
       reason: a 403 here would confirm the node exists to someone who may not
       know that (§6.3).
    2. **Restricted node → 403, audited.** Not because the caller lacks the
       grant — they may well hold it — but because an outbound message composed
       from restricted material is an exfiltration path, and the honest way to
       close it is for the path not to exist. This is the one refusal that
       fires *against* a principal who is otherwise allowed.
    3. **Non-person node → 400.** Outreach addresses a person. Drafting one for
       a Document produces a message to nobody.

    Everything the body says comes from edges this principal can already
    traverse, so the draft can never carry a fact its author could not read.
    """
    indexed = instance.index.get_node(body.node_id)
    if indexed is None or not access.allows(indexed.acl_ref, indexed.sensitivity):
        raise HTTPException(404, "not found")

    if indexed.sensitivity is Sensitivity.RESTRICTED:
        audit.record(
            actor=principal,
            action=Action.OUTREACH_REFUSED,
            outcome=Outcome.REFUSED,
            node_ids=[indexed.id],
            detail="restricted content may not be drafted into outreach",
        )
        raise HTTPException(403, "restricted content cannot be drafted into outreach")

    if indexed.type not in (str(NodeType.PERSON), str(NodeType.ACCOUNT)):
        raise HTTPException(400, f"{indexed.type} is not a person; outreach needs one")

    facts = _visible_facts(instance, access, indexed)
    provider = choose_lead_source()
    org = _organization(instance, access, indexed)
    try:
        lead = provider.source.find(indexed.title, organization=org)
    except ApolloError as exc:
        # A lookup failure is not a draft failure — the graph facts stand on
        # their own. Recorded so a silently key-less deployment is visible.
        audit.record(
            actor=principal,
            action=Action.OUTREACH_DRAFT,
            outcome=Outcome.ERROR,
            node_ids=[indexed.id],
            detail=f"lead lookup failed: {exc}",
        )
        lead = None

    subject, text = compose(
        node_title=indexed.title,
        node_type=indexed.type,
        facts=facts,
        lead=lead,
        sender_display=principal.display,
    )
    store = OutreachStore(instance.repo)
    draft = store.put(
        OutreachDraft(
            draft_id=draft_id(indexed.id, principal.id, text),
            node_id=indexed.id,
            node_title=indexed.title,
            sensitivity=indexed.sensitivity,
            drafted_by=principal.id,
            created_at=datetime.now(UTC),
            subject=subject,
            body=text,
            facts=tuple(facts),
            lead=lead,
            lead_source=provider.source.name,
        )
    )
    audit.record(
        actor=principal,
        action=Action.OUTREACH_DRAFT,
        outcome=Outcome.OK,
        node_ids=[indexed.id],
        proposal_id=draft.draft_id,
        detail=f"{len(facts)} fact(s), lead via {provider.source.name}",
    )
    return _outreach_out(draft)


@api.post("/api/outreach/send", response_model=OutreachOut)
def outreach_send(
    body: OutreachSendIn,
    instance: Annotated[App, Depends(get_app)],
    access: Annotated[AccessFilter, Depends(get_access)],
    principal: Annotated[Principal, Depends(get_reviewer)],
    audit: Annotated[AuditLog, Depends(get_audit)],
) -> OutreachOut:
    """Dispatch an approved draft. Only an approved one.

    The state check lives in `OutreachStore.dispatch`, so a pending or rejected
    id is refused by the store rather than by a condition in this handler that
    a second caller could forget to repeat.

    The visibility re-check is not redundant with the draft-time one. Grants are
    mirrored from source systems and are eventually consistent by construction
    (`acl/grants.py`), so a principal can lose access between drafting and
    sending — and the send is the irreversible half. A draft whose subject the
    sender can no longer see does not go out.

    **No message is transmitted.** Apollo is wired for lead lookup only. This
    records an approved dispatch and audits it; when a send channel lands it
    plugs in behind these same guards.
    """
    store = OutreachStore(instance.repo)
    try:
        draft = store.get(body.draft_id)
    except OutreachError as exc:
        raise HTTPException(404, str(exc)) from exc

    indexed = instance.index.get_node(draft.node_id)
    if indexed is None or not access.allows(indexed.acl_ref, indexed.sensitivity):
        audit.record(
            actor=principal,
            action=Action.OUTREACH_REFUSED,
            outcome=Outcome.NOT_FOUND,
            proposal_id=draft.draft_id,
            detail="sender can no longer see the subject of this draft",
        )
        raise HTTPException(404, "not found")

    try:
        sent = store.dispatch(body.draft_id, sender=principal.id)
    except OutreachError as exc:
        audit.record(
            actor=principal,
            action=Action.OUTREACH_REFUSED,
            outcome=Outcome.REFUSED,
            node_ids=[draft.node_id],
            proposal_id=draft.draft_id,
            detail=str(exc),
        )
        raise HTTPException(409, str(exc)) from exc

    audit.record(
        actor=principal,
        action=Action.OUTREACH_SEND,
        outcome=Outcome.OK,
        node_ids=[sent.node_id],
        proposal_id=sent.draft_id,
        detail=f"approved by {sent.decided_by}, dispatched by {principal.id}",
    )
    return _outreach_out(sent)


@api.get("/api/outreach", response_model=list[OutreachOut])
def outreach_list(
    instance: Annotated[App, Depends(get_app)],
    access: Annotated[AccessFilter, Depends(get_access)],
    state: str | None = None,
) -> list[OutreachOut]:
    """Drafts, ACL-projected on the way out.

    A draft is filtered by whether the *reader* can see its subject, not by who
    wrote it: the draft body quotes the graph, so listing one to a principal
    who cannot open the node it came from would route around the node's ACL.
    """
    store = OutreachStore(instance.repo)
    wanted = OutreachState(state) if state else None
    out: list[OutreachOut] = []
    for draft in store.records(state=wanted):
        indexed = instance.index.get_node(draft.node_id)
        if indexed is None or not access.allows(indexed.acl_ref, indexed.sensitivity):
            continue
        out.append(_outreach_out(draft))
    return out


def _organization(instance: App, access: AccessFilter, node: IndexedNode) -> str | None:
    """The team this person belongs to, if the principal can see it.

    Passed to Apollo to disambiguate a common name. Skipped when the edge
    points somewhere invisible — narrowing a lead lookup with a team name the
    caller cannot read would leak it into a third party's query log.
    """
    # Adjacency, not frontmatter — see `_visible_facts` for why an entity node's
    # own relations are empty.
    for predicate, obj in instance.index.edges_of(node.id):
        if predicate != "member_of":
            continue
        target = instance.index.get_node(obj)
        if target is not None and access.allows(target.acl_ref, target.sensitivity):
            return target.title
    return None


# Inbound edges point *at* the person, so reading them out unchanged produces
# fragments — "Quarterly close runbook — authored by". Each entry inverts the
# relation into a sentence with the person as its subject. A predicate with no
# entry falls back to naming the relation rather than guessing at English.
_INBOUND_PHRASE: dict[str, str] = {
    "authored_by": "authored {title}",
    "mentions": "mentioned in {title}",
    "owns": "owned by {title}",
    "operated_by": "operates {title}",
    "handoff_to": "receives handoffs from {title}",
    "depends_on": "depended on by {title}",
}


def _visible_facts(instance: App, access: AccessFilter, node: IndexedNode) -> list[str]:
    """Graph statements about this person, filtered to what the caller can see.

    Reads the index adjacency rather than the node's own frontmatter: an entity
    node carries no relations of its own, so everything the graph knows about a
    person arrives as edges pointing *at* them. Drafting from `node.edges`
    produces an empty message for every Person in the corpus.

    Only accepted edges (invariant 10). The informative predicates for a person
    — `owns` above all — are exactly the ones §11 holds back for review, so a
    draft that used proposed edges would put the system's unreviewed guesses
    into a message addressed to the person they are about. What survives is
    weaker and true, which is the right trade here.

    Outbound first: `mentions` is the most common edge and the least
    informative (CLAUDE.md), and an unweighted list of it drowns everything
    else.
    """
    facts: list[str] = []
    # Deduped on the rendered sentence, not on the node id. Two documents can
    # share a title ("Re: Security review — status" appears twice in the
    # corpus), and a reviewer reading the same line twice cannot tell a real
    # repetition from a bug.
    seen: set[str] = set()

    def title_of(other_id: str) -> str | None:
        other = instance.index.get_node(other_id)
        if other is None or not access.allows(other.acl_ref, other.sensitivity):
            return None
        return other.title

    def add(sentence: str) -> None:
        if sentence not in seen:
            seen.add(sentence)
            facts.append(sentence)

    for predicate, obj in instance.index.edges_of(node.id):
        if len(facts) >= MAX_FACTS:
            return facts
        title = title_of(obj)
        if title is not None:
            add(f"{predicate.replace('_', ' ')} {title}")

    for predicate, subject in instance.index.edges_into(node.id):
        if len(facts) >= MAX_FACTS:
            return facts
        title = title_of(subject)
        if title is None:
            continue
        template = _INBOUND_PHRASE.get(predicate, f"{{title}} — {predicate.replace('_', ' ')}")
        add(template.format(title=title))
    return facts


@api.get("/api/review", response_model=list[PendingOut])
def review_pending(
    instance: Annotated[App, Depends(get_app)],
    predicate: str | None = None,
    limit: int = 100,
) -> list[PendingOut]:
    """The queue: agent proposals first, then extraction-proposed edges.

    Agent proposals lead because they are the smaller, newer, and more
    consequential pile — an agent's suggestion is unreviewed input from outside
    the system, where an extraction-proposed edge is the system reporting its
    own uncertainty about a document a human already trusted.
    """
    from company_brain.review.queue import ReviewQueue

    queue = ReviewQueue(instance.repo)
    out: list[PendingOut] = []

    for diff in queue.pending_proposals(predicate):
        record = diff.record
        out.append(
            PendingOut(
                key=record.proposal_id,
                kind="proposal",
                node_id=record.target,
                node_title=diff.target_title,
                predicate=record.predicate,
                subject=None,
                subject_title=None,
                object=record.object,
                confidence=None,
                quote="",
                summary=record.summary,
                proposed_by=record.proposed_by,
                delegated_by=record.delegated_by,
                stale=diff.stale,
                body_diff=[DiffLineOut(kind=c.kind, text=c.text) for c in diff.body],
                added_relations=[_relation_out(instance, e) for e in diff.added_relations],
                removed_relations=[_relation_out(instance, e) for e in diff.removed_relations],
            )
        )

    # Outreach next. Ahead of extraction edges for the same reason agent
    # proposals are: this is the only queue item that, once approved, results
    # in contacting a person. `predicate` does not apply to it — an outreach
    # draft has no predicate — so a predicate-filtered queue omits it rather
    # than pretending one.
    if predicate is None:
        store = OutreachStore(instance.repo)
        for draft in store.records(state=OutreachState.PENDING):
            out.append(
                PendingOut(
                    key=draft.draft_id,
                    kind="outreach",
                    node_id=draft.node_id,
                    node_title=draft.node_title,
                    predicate=None,
                    subject=None,
                    subject_title=None,
                    object=None,
                    confidence=None,
                    quote="",
                    summary=draft.subject,
                    proposed_by=draft.drafted_by,
                    delegated_by=None,
                    outreach=_outreach_out(draft),
                )
            )

    for item in queue.pending_edges(predicate)[: max(0, limit - len(out))]:
        out.append(
            PendingOut(
                key=item.key,
                kind="edge",
                node_id=item.node_id,
                node_title=item.node_title,
                predicate=str(item.edge.predicate),
                subject=item.edge.subject,
                subject_title=_title(instance, item.edge.subject),
                object=item.edge.object,
                confidence=item.edge.confidence,
                quote=item.quote(),
                summary=f"{item.edge.subject or item.node_id} "
                f"-{item.edge.predicate}-> {item.edge.object}",
                # An extraction-proposed edge is a one-line diff: nothing is
                # removed, one relation is added.
                added_relations=[_relation_out(instance, item.edge)],
            )
        )
    return out


@api.get("/api/review/stats", response_model=ReviewStatsOut)
def review_stats(instance: Annotated[App, Depends(get_app)]) -> ReviewStatsOut:
    from company_brain.review.queue import ReviewQueue

    queue = ReviewQueue(instance.repo)
    stats = queue.stats()
    outreach = OutreachStore(instance.repo)
    waiting = len(outreach.records(state=OutreachState.PENDING))
    return ReviewStatsOut(
        pending=stats.total + stats.proposals + waiting,
        pending_proposals=stats.proposals,
        pending_outreach=waiting,
        by_predicate=stats.by_predicate,
        accept_rate={k: [a, d] for k, (a, d) in queue.accept_rate().items()},
        proposal_accept_rate={k: [a, d] for k, (a, d) in queue.proposals.accept_rate().items()},
        outreach_accept_rate={k: [a, d] for k, (a, d) in outreach.accept_rate().items()},
    )


@api.post("/api/review/decide")
def review_decide(
    body: DecideIn,
    instance: Annotated[App, Depends(get_app)],
    reviewer: Annotated[Principal, Depends(get_reviewer)],
    audit: Annotated[AuditLog, Depends(get_audit)],
) -> dict[str, Any]:
    """Decide one item or five hundred, under the reviewer's own identity.

    Bulk is not a convenience here, it is the acceptance criterion: fifty
    proposals in fifteen minutes means a reviewer who has recognised a pattern
    ("every `mentions` edge on this document is right") must be able to act on
    the pattern rather than re-confirming it fifty times.

    One pass over ``items``, dispatching on the tag the queue itself supplied.
    Consecutive edges accumulate and flush together, because ``decide_many``
    groups them by node and pays for one store write per node rather than one
    per edge — the reviewer's order survives, and so does the batching.
    """
    from company_brain.review.proposals import ProposalError, StaleProposalError
    from company_brain.review.queue import Decision, ReviewQueue

    if body.decision not in ("accepted", "rejected", "pending"):
        raise HTTPException(400, "decision must be 'accepted', 'rejected', or 'pending'")
    if not body.items:
        raise HTTPException(400, "nothing to decide")

    decision = Decision(body.decision)
    queue = ReviewQueue(instance.repo, audit=audit)
    run: list[str] = []

    outreach = OutreachStore(instance.repo)

    try:
        for item in body.items:
            if item.kind == "edge":
                run.append(item.key)
                continue
            if run:
                queue.decide_many(run, decision, reviewer=reviewer)
                run = []
            if item.kind == "outreach":
                _decide_outreach(outreach, item.key, decision, reviewer, audit)
                continue
            queue.decide_proposal(item.key, decision, reviewer=reviewer)
        if run:
            queue.decide_many(run, decision, reviewer=reviewer)
    except StaleProposalError as exc:
        # 409, not 404: the item is there, the world moved. The distinction is
        # what tells the reviewer to re-read rather than to go looking.
        raise HTTPException(409, str(exc)) from exc
    except OutreachError as exc:
        audit.record(
            actor=reviewer,
            action=Action.OUTREACH_REFUSED,
            outcome=Outcome.ERROR,
            detail=str(exc),
        )
        raise HTTPException(409, str(exc)) from exc
    except (KeyError, ValueError, ProposalError) as exc:
        failed = Action.REVIEW_REJECT if decision is Decision.REJECTED else Action.REVIEW_ACCEPT
        audit.record(actor=reviewer, action=failed, outcome=Outcome.ERROR, detail=str(exc))
        raise HTTPException(404, str(exc)) from exc

    mark_index_stale()
    return {"decided": len(body.items), "decision": body.decision, "by": reviewer.id}


@api.get("/api/audit", response_model=list[AuditOut])
def audit_trail(
    audit: Annotated[AuditLog, Depends(get_audit)],
    actor: str | None = None,
    node_id: str | None = None,
    limit: int = 100,
) -> list[AuditOut]:
    """Who saw what, when.

    Unfiltered by principal, and deliberately so: this is an operator surface,
    and an audit log each actor can filter to their own good behaviour is not
    one. It returns node IDs and never node content (invariant 15), so reading
    it discloses the shape of activity, not the material.
    """
    return [
        AuditOut(**{**record.to_dict(), "node_ids": list(record.node_ids)})
        for record in audit.read(limit=min(limit, 500), actor=actor, node_id=node_id)
    ]


@api.get("/api/audit/stats")
def audit_stats(audit: Annotated[AuditLog, Depends(get_audit)]) -> dict[str, int]:
    return summarize(audit.scan())


# ---- live collaboration -------------------------------------------------
#
# Demo-grade: server-authoritative, last-write-wins, no CRDT. See
# docs/ARCHITECTURE.md §15 and company_brain/collab/session.py.

SUBPROTOCOL_PREFIX = "cb.principal."
# One code for "gone" and "not yours" alike. Distinguishing them would confirm a
# node exists to someone who cannot read it (§6.3), which is the same reason
# `get_node` 404s rather than 403s.
CLOSE_NOT_VISIBLE = 4404
CLOSE_BAD_IDENTITY = 4401


@lru_cache(maxsize=1)
def _hub(store: str = str(STORE_ROOT)) -> CollabHub:
    return CollabHub(SessionRegistry(_app(store).repo))


def get_hub() -> CollabHub:
    return _hub()


def principal_from_subprotocol(websocket: WebSocket) -> str | None:
    """Read the principal out of the WebSocket subprotocol.

    A browser cannot set `X-Principal` on a WebSocket, so the header stand-in
    does not carry over. The subprotocol is the closest equivalent: it is fixed
    at connect time and cannot be restated per message, which is what invariant
    8 actually requires — identity arrives out-of-band and is never a parameter
    the caller can vary to become somebody else.

    Still a demo stand-in for a session cookie, exactly as `X-Principal` is.
    """
    # scope is a plain dict, so subprotocols come back untyped.
    offered_list: list[str] = list(websocket.scope.get("subprotocols", []))
    for offered in offered_list:
        if offered.startswith(SUBPROTOCOL_PREFIX):
            candidate = offered[len(SUBPROTOCOL_PREFIX) :]
            if candidate in PRINCIPALS:
                return candidate
    return None


@api.websocket("/api/collab/node/{node_id:path}")
async def collab_node(
    websocket: WebSocket,
    node_id: str,
    instance: Annotated[App, Depends(get_app)],
    hub: Annotated[CollabHub, Depends(get_hub)],
) -> None:
    """Live editing for one node's human-authored text."""
    name = principal_from_subprotocol(websocket)
    if name is None:
        await websocket.accept()
        await websocket.close(CLOSE_BAD_IDENTITY, "unknown or missing principal")
        return

    await websocket.accept(subprotocol=f"{SUBPROTOCOL_PREFIX}{name}")
    access = instance.access(PRINCIPALS[name])

    indexed = instance.index.get_node(node_id)
    if indexed is None or not access.allows(indexed.acl_ref, indexed.sensitivity):
        await websocket.close(CLOSE_NOT_VISIBLE, "not found, or not visible to you")
        return

    try:
        room = hub.registry.open(node_id)
    except NodeNotFoundError:
        # Indexed but absent from the store: drift, not a permission problem.
        await websocket.close(CLOSE_NOT_VISIBLE, "not found, or not visible to you")
        return

    connection = hub.next_connection_id()
    room.join(connection, name, PRINCIPALS[name].display)
    hub.attach(node_id, connection, websocket)

    await websocket.send_json(
        {
            "type": "welcome",
            "connection": connection,
            "revision": room.revision,
            "body": room.body,
            "participants": room.presence(),
        }
    )
    await hub.announce_presence(room)

    try:
        while True:
            message = await websocket.receive_json()
            kind = message.get("type")

            if kind == "edit":
                try:
                    outcome = room.apply_edit(
                        connection,
                        int(message.get("base_revision", room.revision)),
                        str(message.get("body", "")),
                    )
                except FenceViolation as exc:
                    # Refuse and resync. The browser is not a trust boundary.
                    await websocket.send_json(
                        {
                            "type": "rejected",
                            "reason": str(exc),
                            "revision": room.revision,
                            "body": room.body,
                        }
                    )
                    continue
                await hub.broadcast(
                    node_id,
                    {
                        "type": "sync",
                        "revision": outcome.revision,
                        "body": outcome.body,
                        "by": connection,
                        "clobbered": outcome.clobbered,
                    },
                )
                hub.schedule_flush(node_id)

            elif kind == "cursor":
                room.move_cursor(
                    connection, int(message.get("anchor", 0)), int(message.get("head", 0))
                )
                await hub.announce_presence(room)

    except WebSocketDisconnect:
        pass
    finally:
        room.leave(connection)
        hub.detach(node_id, connection)
        if room.empty:
            # Flush and rebuild once the last editor leaves, not per keystroke:
            # re-indexing 232 nodes on every character would make the demo crawl.
            if await hub.shutdown_room(node_id):
                _app.cache_clear()
        else:
            await hub.announce_presence(room)


ASK_ROOM = "__ask__"


@api.websocket("/api/collab/ask")
async def collab_ask(
    websocket: WebSocket,
    instance: Annotated[App, Depends(get_app)],
    hub: Annotated[CollabHub, Depends(get_hub)],
) -> None:
    """One shared ask session the whole team sits inside.

    A question asked by anyone is answered for *everyone* — but each answer is
    computed against the asking-back principal's own grants, never the asker's.
    Broadcasting one principal's answer to the room would be a leak wearing a
    collaboration costume, and it is the obvious way to get this wrong.
    """
    name = principal_from_subprotocol(websocket)
    if name is None:
        await websocket.accept()
        await websocket.close(CLOSE_BAD_IDENTITY, "unknown or missing principal")
        return

    await websocket.accept(subprotocol=f"{SUBPROTOCOL_PREFIX}{name}")
    connection = hub.next_connection_id()
    hub.attach(ASK_ROOM, connection, websocket, principal=name)

    await websocket.send_json({"type": "welcome", "connection": connection})
    await _announce_ask_room(hub)

    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") != "ask":
                continue
            question = str(message.get("question", "")).strip()
            if not question:
                continue
            limit = int(message.get("limit", 6))

            await hub.broadcast(
                ASK_ROOM,
                {"type": "asking", "question": question, "by": PRINCIPALS[name].display},
            )

            # Fan out per participant, each under their own grants. Sequential
            # on purpose: with a live synthesizer this is one model call each,
            # and a room of four should not open four at once.
            for peer, peer_principal in hub.members(ASK_ROOM).items():
                access = instance.access(PRINCIPALS[peer_principal])
                try:
                    result = await asyncio.to_thread(
                        answer_for, instance, access, question, limit
                    )
                    payload = result.model_dump()
                except CitationLeakBlocked as exc:
                    payload = {"question": question, "refused": f"citation leak blocked: {exc}"}
                await hub.send_to(ASK_ROOM, peer, {"type": "answer", **payload})

    except WebSocketDisconnect:
        pass
    finally:
        hub.detach(ASK_ROOM, connection)
        await _announce_ask_room(hub)


async def _announce_ask_room(hub: CollabHub) -> None:
    participants = [
        {
            "connection": conn,
            "principal": principal,
            "display": PRINCIPALS[principal].display,
            "color": participant_color(principal),
        }
        for conn, principal in hub.members(ASK_ROOM).items()
    ]
    await hub.broadcast(ASK_ROOM, {"type": "presence", "participants": participants})


api.include_router(gmail_oauth_router, tags=["gmail"])
api.include_router(gmail_routes_router)

app = api
