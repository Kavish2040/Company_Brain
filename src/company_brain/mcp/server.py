"""MCP server: the agent-facing surface.

Three rules from ARCHITECTURE §8, all enforced here rather than documented:

* **Identity is never a tool parameter.** The principal comes from the session,
  so an agent cannot say "I am acting as the CFO". Every tool signature below
  takes its principal from the bound session, not from the model's arguments.
* **Agents never write to the graph.** `write_node` and `propose_edge` create
  entries under `store/_proposals/` plus a queue row, and return a proposal ID.
  The store this module holds is a :class:`ProposalOnlyStore`, not a
  ``Repository`` — the mutating half of the API is present and refusing, so a
  direct write attempt is an audited event rather than a missing method.
* **Every call is audited.** ``(principal, delegated_by, tool, node_ids)`` —
  IDs, never content (invariant 15). Reads too, not just writes: "who saw what,
  when" is an M5 requirement, and the part of it that cannot be backfilled is
  the part that starts today.

What an agent can do here that it could not before is propose. What it still
cannot do — and the reason proposing is safe — is widen. A proposal inherits
the narrowest tier of everything it draws on, and a proposal that would sit
above that tier is *blocked*, not queued: ARCHITECTURE §11's table ends with
"anything that would widen an ACL → hard block, not a proposal", and a queued
widening is a widening with a reviewer's name attached.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from company_brain.acl.grants import AccessFilter
from company_brain.app import App
from company_brain.audit.log import Action, AuditLog, Outcome, Surface
from company_brain.mcp.guard import (
    AclWideningBlocked,
    AgentWriteRefused,
    NotVisible,
    PatchFieldRefused,
    ProposalOnlyStore,
)
from company_brain.retrieve.hybrid import HybridRetriever
from company_brain.review.proposals import (
    ProposalKind,
    ProposalRecord,
    ProposalStore,
    proposal_id,
)
from company_brain.schemas.acl import Principal, PrincipalKind
from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance
from company_brain.schemas.nodes import Node

__all__ = [
    "AclWideningBlocked",
    "AgentWriteRefused",
    "McpTools",
    "NotVisible",
    "PatchFieldRefused",
    "Session",
    "describe",
]

# An agent proposes; it never asserts. Confidence is fixed rather than accepted
# as an argument: a model asked to rate its own certainty will produce whatever
# number gets its edge accepted, and §11's gates are only as good as the inputs
# they gate on. A human reading the evidence is the confidence signal here.
AGENT_CONFIDENCE = 0.5


class SessionNotAuthorized(PermissionError):
    """The agent is not registered, or the human it claims is unknown."""


@dataclass(slots=True)
class Session:
    """An authenticated MCP session.

    ``agent_id`` is the agent's own identity; ``delegated_by`` is the human who
    invoked it. The effective visible set is the intersection (invariant 8),
    computed in GrantTable — not here, so there is one implementation of it.

    Bound once, at startup, by :meth:`bind`. Everything a tool needs to know
    about who is calling is fixed at that moment: nothing below reads identity
    from a request, because for a stdio server the *process* is the session.

    ``read_only`` exists because "may this agent propose" is a per-deployment
    question with no safe default in either direction. A proposal changes
    nothing a reader can see, so allowing it does not need to fail closed; but
    an agent wired to a source it should only summarize has no business filling
    a reviewer's queue either. So it is explicit, and it is bound here rather
    than checked at the tool, for the same reason the principal is.
    """

    app: App
    agent_id: str
    delegated_by: str
    audit: AuditLog
    read_only: bool = False

    @classmethod
    def bind(
        cls,
        app: App,
        *,
        agent_id: str,
        delegated_by: str,
        read_only: bool = False,
        audit: AuditLog | None = None,
    ) -> Session:
        """Register and validate a session, then freeze it.

        Registration happens before the session exists because an unregistered
        agent is denied everything — correct, but it would surface as silently
        empty results rather than as a refusal, and "the tool returned nothing"
        is the single most expensive way to learn about a misconfiguration.
        """
        human = Principal(id=delegated_by, kind=PrincipalKind.USER, display=delegated_by)
        if not app.grants.visible_refs(human):
            # A human holding no grants at all is almost certainly a typo'd
            # name. Binding to them yields a session that can see nothing and
            # explain nothing, which is the most expensive way to learn about a
            # misconfiguration — so it fails at startup, loudly.
            raise SessionNotAuthorized(
                f"{delegated_by!r} holds no grants; check the --as principal"
            )
        app.grants.register_agent(agent_id, inherit=True)
        log = audit if audit is not None else app.audit(Surface.MCP)
        session = cls(
            app=app,
            agent_id=agent_id,
            delegated_by=delegated_by,
            audit=log,
            read_only=read_only,
        )
        log.record(
            actor=session.principal,
            action=Action.SESSION_OPENED,
            outcome=Outcome.OK,
            detail=(
                f"{len(session.access.refs)} visible refs, "
                f"{'read-only' if read_only else 'may propose'}"
            ),
        )
        return session

    @property
    def principal(self) -> Principal:
        return Principal(
            id=self.agent_id,
            kind=PrincipalKind.AGENT,
            display=f"agent {self.agent_id}",
            delegated_by=self.delegated_by,
        )

    @property
    def access(self) -> AccessFilter:
        """A fresh filter per call.

        `AccessFilter` resolves the visible set once at construction, so a
        long-lived one would pin an agent's permissions to whatever they were
        when the process started — and a grant revoked mid-session has to take
        effect, which is the M2 property this would quietly undo.
        """
        return self.app.access(self.principal)

    @property
    def store(self) -> ProposalOnlyStore:
        """The only store the tools can reach.

        Rebuilt per access so it carries a current access filter, for the same
        reason as above. Cheap: it holds references, not data.
        """
        return ProposalOnlyStore(
            self.app.repo,
            index=self.app.index,
            access=self.access,
            principal=self.principal,
            audit=self.audit,
            proposals=ProposalStore(self.app.repo),
            may_propose=not self.read_only,
        )


class McpTools:
    """The five tools. Read tools ACL-filter; write tools produce proposals."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ---- read ----------------------------------------------------------

    def search(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        retriever = HybridRetriever(self.session.app.index, self.session.access)
        result = retriever.retrieve(query, limit=limit)
        found = [
            {
                "node_id": node.node_id,
                "title": node.title,
                "score": round(node.score, 5),
                "snippet": node.snippets[0][:300] if node.snippets else "",
                "hops": node.hops,
            }
            for node in result.nodes
        ]
        # The query is not logged. It is user-supplied prose, which invariant 15
        # keeps out of the log for the same reason document text is: a question
        # about the acquisition is content about the acquisition.
        self._audit(Action.SEARCH, Outcome.OK, [node.node_id for node in result.nodes])
        return found

    def traverse(
        self, node_id: str, predicates: list[str] | None = None, limit: int = 20
    ) -> list[dict[str, str]]:
        index = self.session.app.index
        access = self.session.access
        wanted = frozenset(predicates) if predicates else None
        out: list[dict[str, str]] = []
        for neighbour in index.neighbours(node_id, wanted, limit=limit * 2):
            indexed = index.get_node(neighbour)
            # Filter per hop, not once at the seed.
            if indexed is None or not access.allows(indexed.acl_ref, indexed.sensitivity):
                continue
            out.append({"node_id": indexed.id, "title": indexed.title, "type": indexed.type})
            if len(out) >= limit:
                break
        self._audit(Action.TRAVERSE, Outcome.OK, [node_id, *(n["node_id"] for n in out)])
        return out

    def read_node(self, node_id: str) -> dict[str, Any]:
        """Return the ACL-projected node — never the stored bytes.

        A node whose every edge is invisible returns not-found rather than an
        empty page: an empty page confirms the node exists (§6.3).
        """
        index = self.session.app.index
        access = self.session.access
        try:
            node = self.session.store.visible(node_id)
        except NotVisible:
            self._audit(Action.READ_NODE, Outcome.NOT_FOUND, [node_id])
            raise KeyError(node_id) from None

        indexed = index.get_node(node_id)
        if indexed is None:  # unreachable: `visible` resolved it through the index
            raise KeyError(node_id)

        visible_edges = []
        for edge in indexed.edges:
            if edge.status is not EdgeStatus.ACCEPTED:
                continue
            target = index.get_node(edge.object)
            if target is None or not access.allows(target.acl_ref, target.sensitivity):
                continue
            visible_edges.append(
                {
                    "predicate": str(edge.predicate),
                    "object": edge.object,
                    "confidence": edge.confidence,
                    "provenance": str(edge.provenance),
                }
            )

        self._audit(Action.READ_NODE, Outcome.OK, [node_id])
        return {
            "id": indexed.id,
            "type": indexed.type,
            "title": indexed.title,
            "body": node.body,
            "sensitivity": str(indexed.sensitivity),
            "relations": visible_edges,
        }

    # ---- write (proposals only) -----------------------------------------

    def write_node(self, node_id: str, patch: dict[str, Any]) -> dict[str, str]:
        """Propose a change to a node's human-authored text.

        Everything that makes this safe happens before a byte is written:

        1. The node must be *visible to this session*. Proposing against a node
           you cannot read is an existence oracle, and it was the hole in the
           previous version of this method — it went straight to ``repo.find``.
        2. The patch may name only agent-writable fields. An ACL field is a
           blocked widening attempt, not an ignored key.
        3. The proposal inherits the node's own tier, and its ACL block is
           copied, not composed — an agent has no vocabulary for expressing one.
        4. Generated regions must survive byte-identically (invariant 13).
        """
        store = self.session.store
        try:
            node = store.visible(node_id)
        except NotVisible:
            self._audit(Action.WRITE_NODE, Outcome.NOT_FOUND, [node_id])
            raise KeyError(node_id) from None

        store.check_patch(patch, node_id)

        frontmatter = node.frontmatter
        if "aliases" in patch:
            aliases = tuple(dict.fromkeys(str(a) for a in patch["aliases"]))
            frontmatter = frontmatter.model_copy(update={"aliases": aliases})
        proposed = Node(frontmatter=frontmatter, body=str(patch.get("body", node.body)))
        _acl_unchanged(node, proposed)
        store.check_generated_regions(node, proposed)

        record = self._record(
            ProposalKind.NODE_BODY,
            target=node_id,
            payload=proposed.body,
            sensitivity=store.inherited_tier(node_id),
            base=store.base_sha256(node),
            summary=f"body edit to {frontmatter.title}",
        )
        stored = store.propose(record, proposed)
        self._audit(Action.WRITE_NODE, Outcome.OK, [node_id], proposal_id=stored.proposal_id)
        return {"proposal_id": stored.proposal_id, "state": "pending_review"}

    def propose_edge(
        self, subject: str, predicate: str, obj: str, evidence_quote: str
    ) -> dict[str, str]:
        """Propose a typed edge, with a verbatim quote as evidence.

        Both ends must be visible to this session, and the proposal inherits
        ``narrowest(subject, object)``. That second rule is the one doing real
        work: an edge from an internal document to a restricted node, written at
        internal tier, publishes the existence and ID of restricted content to
        everyone holding the internal grant. It is a widening even though no
        restricted *prose* moved, and it is blocked rather than queued.
        """
        store = self.session.store
        try:
            node = store.visible(subject)
            store.visible(obj)
        except NotVisible as exc:
            self._audit(Action.PROPOSE_EDGE, Outcome.NOT_FOUND, [subject])
            raise KeyError(str(exc.args[0])) from None

        try:
            resolved = Predicate(predicate)
        except ValueError as exc:
            self._audit(
                Action.PROPOSE_EDGE, Outcome.ERROR, [subject], detail="unknown predicate"
            )
            raise ValueError(
                f"unknown predicate {predicate!r}; one of {[str(p) for p in Predicate]}"
            ) from exc

        edge = Edge(
            predicate=resolved,
            # A document is never the subject of a third-party relation, so the
            # subject is stated explicitly and the edge lives on the node that
            # carries the evidence.
            object=obj,
            confidence=AGENT_CONFIDENCE,
            provenance=Provenance.LLM,
            # Always proposed. There is no argument an agent can pass that makes
            # this accepted.
            status=EdgeStatus.PROPOSED,
            evidence=(Evidence(node=subject, quote=evidence_quote[:500]),),
        )
        merged = {e.sort_key(): e for e in node.frontmatter.relations}
        merged[edge.sort_key()] = edge
        proposed = Node(
            frontmatter=node.frontmatter.model_copy(
                update={"relations": tuple(merged.values())}
            ),
            body=node.body,
        )
        _acl_unchanged(node, proposed)

        record = self._record(
            ProposalKind.EDGE,
            target=subject,
            payload=f"{predicate}\0{obj}",
            sensitivity=store.inherited_tier(subject, obj),
            base=store.base_sha256(node),
            summary=f"{subject} -{predicate}-> {obj}",
            predicate=str(resolved),
            obj=obj,
        )
        stored = store.propose(record, proposed)
        self._audit(
            Action.PROPOSE_EDGE,
            Outcome.OK,
            [subject, obj],
            proposal_id=stored.proposal_id,
        )
        return {"proposal_id": stored.proposal_id, "state": "pending_review"}

    # ---- internals -------------------------------------------------------

    def _record(
        self,
        kind: ProposalKind,
        *,
        target: str,
        payload: str,
        sensitivity: Any,
        base: str,
        summary: str,
        predicate: str | None = None,
        obj: str | None = None,
    ) -> ProposalRecord:
        session = self.session
        return ProposalRecord(
            proposal_id=proposal_id(kind, session.agent_id, target, payload),
            kind=kind,
            target=target,
            proposed_by=session.agent_id,
            delegated_by=session.delegated_by,
            surface=str(Surface.MCP),
            created_at=_now(),
            base_sha256=base,
            sensitivity=sensitivity,
            predicate=predicate,
            object=obj,
            summary=summary,
        )

    def _audit(
        self,
        action: Action,
        outcome: Outcome,
        node_ids: list[str],
        *,
        proposal_id: str | None = None,
        detail: str = "",
    ) -> None:
        self.session.audit.record(
            actor=self.session.principal,
            action=action,
            outcome=outcome,
            node_ids=node_ids,
            proposal_id=proposal_id,
            detail=detail,
        )


def _now() -> datetime:
    return datetime.now(UTC)


def _acl_unchanged(before: Node, after: Node) -> None:
    """The postcondition that makes "structurally unable to widen" a fact.

    Whatever a patch said, the proposed node's ACL block is the one already on
    the node. Written as a check rather than an ``assert`` on purpose: asserts
    vanish under ``python -O``, and a permission invariant that a runtime flag
    can switch off is not an invariant.
    """
    if before.frontmatter.acl != after.frontmatter.acl:
        raise AclWideningBlocked(
            f"{before.id}: a proposal may not restate a node's ACL "
            f"({before.frontmatter.acl.ref} @ {before.frontmatter.acl.sensitivity})"
        )


def describe() -> dict[str, Any]:
    """Tool manifest. Note the absence of any principal argument."""
    return {
        "server": "company_brain",
        "identity": "from the authenticated session; never a tool parameter",
        "audit": "every call records (principal, delegated_by, tool, node_ids)",
        "tools": [
            {"name": "search", "args": ["query", "limit"], "writes": False},
            {"name": "traverse", "args": ["node_id", "predicates", "limit"], "writes": False},
            {
                "name": "read_node",
                "args": ["node_id"],
                "writes": False,
                "note": "returns an ACL-projected node, never stored bytes",
            },
            {
                "name": "write_node",
                "args": ["node_id", "patch"],
                "writes": "proposal",
                "note": (
                    "patch may set body and aliases only; naming an acl field is "
                    "blocked, not queued"
                ),
            },
            {
                "name": "propose_edge",
                "args": ["subject", "predicate", "object", "evidence_quote"],
                "writes": "proposal",
                "note": "inherits narrowest(subject, object); a widening edge is blocked",
            },
        ],
    }
