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
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from company_brain.acl.grants import AccessFilter
from company_brain.app import PRINCIPALS, STORE_ROOT, App, build_app
from company_brain.collab.guard import FenceViolation
from company_brain.collab.hub import CollabHub
from company_brain.collab.session import SessionRegistry, participant_color
from company_brain.retrieve.hybrid import HybridRetriever
from company_brain.schemas.edges import EdgeStatus
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


class PendingOut(BaseModel):
    key: str
    node_id: str
    node_title: str
    predicate: str
    subject: str | None
    subject_title: str | None
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
            subject=item.edge.subject,
            subject_title=(
                node.title
                if item.edge.subject and (node := instance.index.get_node(item.edge.subject))
                else None
            ),
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


app = api
