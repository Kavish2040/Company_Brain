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

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from company_brain.acl.grants import AccessFilter
from company_brain.app import PRINCIPALS, STORE_ROOT, App, build_app
from company_brain.retrieve.hybrid import HybridRetriever
from company_brain.schemas.edges import EdgeStatus
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


def get_app() -> App:
    return _app()


def get_access(
    instance: Annotated[App, Depends(get_app)],
    x_principal: Annotated[str, Header()] = "ceo",
) -> AccessFilter:
    if x_principal not in PRINCIPALS:
        raise HTTPException(400, f"unknown principal {x_principal!r}")
    return instance.access(PRINCIPALS[x_principal])


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


class PendingOut(BaseModel):
    key: str
    node_id: str
    node_title: str
    predicate: str
    object: str
    confidence: float
    quote: str


class ReviewStatsOut(BaseModel):
    pending: int
    by_predicate: dict[str, int]
    accept_rate: dict[str, list[int]]


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


@api.post("/api/ask", response_model=AskOut)
def ask(
    body: AskIn,
    instance: Annotated[App, Depends(get_app)],
    access: Annotated[AccessFilter, Depends(get_access)],
) -> AskOut:
    retrieval = HybridRetriever(instance.index, access).retrieve(
        body.question, limit=body.limit
    )
    answer = instance.providers.synthesizer().synthesize(
        body.question, retrieval, instance.index
    )

    refused: str | None = None
    try:
        validate(answer, retrieval, access, instance.index)
    except CitationLeakError as exc:
        # Never return the offending text. A leak is surfaced as a refusal.
        raise HTTPException(500, f"citation leak blocked: {exc}") from exc
    except UncitedAnswerError as exc:
        # Invariant 11: an uncited answer is an error, not a degraded response.
        # The UI renders this as a designed error state, not as prose.
        refused = str(exc)
        answer.text = ""
        answer.citations = []

    return AskOut(
        question=body.question,
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
        relations.append(
            EdgeOut(
                predicate=str(edge.predicate),
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


@api.get("/api/review", response_model=list[PendingOut])
def review_pending(
    instance: Annotated[App, Depends(get_app)],
    predicate: str | None = None,
    limit: int = 100,
) -> list[PendingOut]:
    from company_brain.review.queue import ReviewQueue

    return [
        PendingOut(
            key=item.key,
            node_id=item.node_id,
            node_title=item.node_title,
            predicate=str(item.edge.predicate),
            object=item.edge.object,
            confidence=item.edge.confidence,
            quote=item.quote(),
        )
        for item in ReviewQueue(instance.repo).pending_edges(predicate)[:limit]
    ]


@api.get("/api/review/stats", response_model=ReviewStatsOut)
def review_stats(instance: Annotated[App, Depends(get_app)]) -> ReviewStatsOut:
    from company_brain.review.queue import ReviewQueue

    queue = ReviewQueue(instance.repo)
    stats = queue.stats()
    return ReviewStatsOut(
        pending=stats.total,
        by_predicate=stats.by_predicate,
        accept_rate={k: [a, d] for k, (a, d) in queue.accept_rate().items()},
    )


@api.post("/api/review/decide")
def review_decide(
    body: dict[str, str], instance: Annotated[App, Depends(get_app)]
) -> dict[str, str]:
    from company_brain.review.queue import Decision, ReviewQueue

    key, decision = body.get("key", ""), body.get("decision", "")
    if decision not in ("accepted", "rejected"):
        raise HTTPException(400, "decision must be 'accepted' or 'rejected'")
    try:
        ReviewQueue(instance.repo).decide(key, Decision(decision))
    except (KeyError, ValueError) as exc:
        raise HTTPException(404, str(exc)) from exc
    _app.cache_clear()  # the graph changed; next request rebuilds the index
    return {"key": key, "decision": decision}


app = api
