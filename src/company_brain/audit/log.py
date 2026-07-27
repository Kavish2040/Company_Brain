"""The audit log — "who saw what, when".

M5 lists this as an observability requirement, but an audit log that starts in
M5 has nothing to say about M3: you cannot backfill who read a node last
quarter. So it starts at the write path, where the ROADMAP already demands it
("an agent attempting a direct graph write is rejected; the attempt is
audited"), and covers reads from the same day.

Three constraints shape the format.

**Invariant 15 — node IDs, never node content.** Enforced here rather than
trusted to callers: ``node_ids`` is validated against the ID grammar, so prose
cannot be smuggled through it, and ``detail`` is scrubbed to a single short
line. A log that quietly accumulates document text is a second, unguarded copy
of the corpus with none of the ACL machinery around it.

**Invariant 4 — no wall-clock in canonical files.** These are not canonical
files. Like ``store/_sync/``, the log is workflow state: not derived from
markdown, not rebuildable, and explicitly outside invariant 2's "the index is
disposable" rule. It is the one place in the store where wall-clock time is the
*point*, which is why the clock is injected rather than called — a test that
cannot pin time cannot assert on ordering.

**Append-only over a backend that cannot append.** ``StoreBackend`` offers
atomic whole-file writes and nothing else, which is the honest shape for an
object store. So each record is its own immutable file under ``_audit/``, named
``<timestamp>-<digest>.json`` so that lexical order is chronological order and
``walk()`` yields the log already sorted. Rewriting one JSONL file per append
would make every write a read-modify-write race, and would let one corrupt
write destroy the history — the property an audit log exists to have. Production
moves this to an append-only table or object-lock bucket; the record shape is
what should survive that move.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Final

from company_brain.schemas.acl import Principal
from company_brain.schemas.ids import split_id
from company_brain.store.backend import StoreBackend

AUDIT_PREFIX: Final = "_audit"

# A reason, not a payload. Long enough for "owns edge would widen internal ->
# restricted", short enough that no one is tempted to put a document in it.
MAX_DETAIL: Final = 160

# A slug is one or more path segments: document IDs mirror their source tree, so
# `documents/slack/finance/thread-0ac986` is an ordinary ID, not a smuggled path.
_SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]*(?:/[a-z0-9][a-z0-9._-]*)*$")
_WHITESPACE = re.compile(r"\s+")

# Long enough for the deepest real ID, short enough that a paragraph cannot pass
# for one even if it somehow satisfied the grammar.
MAX_NODE_ID = 200


class AuditError(ValueError):
    """A record was malformed — usually content where an ID belongs."""


class Surface(StrEnum):
    """Which door the request came through. Not a permission, a provenance."""

    MCP = "mcp"
    API = "api"
    CLI = "cli"


class Action(StrEnum):
    SESSION_OPENED = "session.opened"
    SEARCH = "search"
    TRAVERSE = "traverse"
    READ_NODE = "read_node"
    WRITE_NODE = "write_node"
    PROPOSE_EDGE = "propose_edge"
    # Refusals. These are the records that matter most, and the reason the log
    # cannot be written by the caller that succeeded.
    GRAPH_WRITE_REFUSED = "graph_write.refused"
    ACL_WIDENING_BLOCKED = "acl_widening.blocked"
    PATCH_FIELD_REFUSED = "patch_field.refused"
    # Human decisions. The reviewer's name on the provenance (ROADMAP M3 demo).
    REVIEW_ACCEPT = "review.accept"
    REVIEW_REJECT = "review.reject"
    REVIEW_REOPEN = "review.reopen"
    PROPOSAL_APPLY = "proposal.apply"
    PROPOSAL_DISCARD = "proposal.discard"


class Outcome(StrEnum):
    OK = "ok"
    REFUSED = "refused"  # the caller asked for something it may not have
    BLOCKED = "blocked"  # structurally impossible, not merely disallowed
    NOT_FOUND = "not_found"  # includes "exists but invisible" — deliberately
    ERROR = "error"


def _scrub(detail: str) -> str:
    """One short line, whitespace collapsed. Never a document."""
    flattened = _WHITESPACE.sub(" ", detail).strip()
    return flattened[:MAX_DETAIL]


def _check_node_id(node_id: str) -> str:
    """Reject anything that is not a node ID.

    This is invariant 15's enforcement point. ``node_ids`` is the field a
    careless caller would reach for to log "context", so it refuses everything
    that is not ``<type_plural>/<slug>`` — where the type segment must be one
    the schema knows and the slug must be lowercase path segments, so no prose
    survives the check.
    """
    if len(node_id) > MAX_NODE_ID:
        raise AuditError(f"audit node_ids takes node IDs only: {len(node_id)} chars")
    try:
        _, slug = split_id(node_id)
    except ValueError as exc:
        raise AuditError(f"audit node_ids takes node IDs only: {exc}") from None
    if not _SLUG.match(slug):
        raise AuditError(f"audit node_ids takes node IDs only, got {node_id!r}")
    return node_id


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """One auditable event.

    ``actor`` and ``delegated_by`` are the pair ARCHITECTURE §8.2 asks for: an
    agent's record names both the agent and the human it acted for, because
    "the research agent read the comp thread" and "the CEO's research agent read
    the comp thread" are different facts and only the second one is true.
    """

    at: datetime
    surface: Surface
    actor: str
    delegated_by: str | None
    action: Action
    outcome: Outcome
    node_ids: tuple[str, ...] = ()
    proposal_id: str | None = None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "at": self.at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "surface": str(self.surface),
            "actor": self.actor,
            "delegated_by": self.delegated_by,
            "action": str(self.action),
            "outcome": str(self.outcome),
            "node_ids": list(self.node_ids),
            "proposal_id": self.proposal_id,
            "detail": self.detail,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> AuditRecord:
        return cls(
            at=datetime.fromisoformat(str(raw["at"]).replace("Z", "+00:00")),
            surface=Surface(raw["surface"]),
            actor=str(raw["actor"]),
            delegated_by=raw.get("delegated_by"),
            action=Action(raw["action"]),
            outcome=Outcome(raw["outcome"]),
            node_ids=tuple(raw.get("node_ids") or ()),
            proposal_id=raw.get("proposal_id"),
            detail=str(raw.get("detail", "")),
        )


def _utc_now() -> datetime:
    return datetime.now(UTC)


class AuditLog:
    """Append-only event log over a :class:`StoreBackend`.

    ``surface`` is bound at construction, not passed per call: the surface is a
    property of the door, and a caller that can name its own surface can claim
    to be a different one.
    """

    def __init__(
        self,
        backend: StoreBackend,
        *,
        surface: Surface,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self.backend = backend
        self.surface = surface
        self._clock = clock

    # ---- write ---------------------------------------------------------

    def record(
        self,
        *,
        actor: Principal | str,
        action: Action,
        outcome: Outcome,
        node_ids: Sequence[str] = (),
        proposal_id: str | None = None,
        detail: str = "",
        delegated_by: str | None = None,
    ) -> AuditRecord:
        """Write one record. Returns it, so a caller can assert on what it wrote.

        Accepts a :class:`Principal` so the delegation pair cannot be split by
        accident — passing a bare string requires naming ``delegated_by``
        yourself, which is what the CLI and API (no delegation) actually want.
        """
        if isinstance(actor, Principal):
            delegated_by = actor.delegated_by
            actor_id = actor.id
        else:
            actor_id = actor

        entry = AuditRecord(
            at=self._clock().astimezone(UTC),
            surface=self.surface,
            actor=actor_id,
            delegated_by=delegated_by,
            action=action,
            outcome=outcome,
            node_ids=tuple(_check_node_id(n) for n in node_ids),
            proposal_id=proposal_id,
            detail=_scrub(detail),
        )
        payload = json.dumps(entry.to_dict(), sort_keys=True, ensure_ascii=False)
        self.backend.write_text(_path_for(entry, payload), payload + "\n")
        return entry

    # ---- read ----------------------------------------------------------

    def read(
        self,
        *,
        limit: int = 100,
        actor: str | None = None,
        action: Action | None = None,
        outcome: Outcome | None = None,
        node_id: str | None = None,
    ) -> list[AuditRecord]:
        """Most recent first — the order a question about an incident is asked in."""
        matched: list[AuditRecord] = []
        for entry in reversed(list(self.scan())):
            if actor is not None and entry.actor != actor:
                continue
            if action is not None and entry.action is not action:
                continue
            if outcome is not None and entry.outcome is not outcome:
                continue
            if node_id is not None and node_id not in entry.node_ids:
                continue
            matched.append(entry)
            if len(matched) >= limit:
                break
        return matched

    def scan(self) -> Iterator[AuditRecord]:
        """Every record, oldest first.

        ``walk`` yields sorted paths and the filenames lead with a fixed-width
        UTC timestamp, so sorted-by-name *is* sorted-by-time. An unparseable
        file is surfaced rather than skipped: silently dropping a record is the
        one failure mode an audit log may not have.
        """
        for path in self.backend.walk(AUDIT_PREFIX):
            if not path.endswith(".json"):
                continue
            text = self.backend.read_text(path)
            if text is None:  # deleted between walk and read
                continue
            try:
                yield AuditRecord.from_dict(json.loads(text))
            except (ValueError, KeyError) as exc:
                raise AuditError(f"corrupt audit record at {path}: {exc}") from exc

    def count(self) -> int:
        return sum(1 for _ in self.scan())


def _path_for(entry: AuditRecord, payload: str) -> str:
    """``_audit/<utc timestamp>-<digest>.json``.

    Fixed-width timestamp first so lexical order is chronological; a digest of
    the payload second so two records in the same microsecond neither collide
    nor overwrite — and so writing the identical record twice is idempotent
    rather than duplicated.
    """
    stamp = entry.at.astimezone(UTC).strftime("%Y%m%dT%H%M%S%f")
    digest = hashlib.blake2b(payload.encode("utf-8"), digest_size=6).hexdigest()
    return f"{AUDIT_PREFIX}/{stamp}-{digest}.json"


def summarize(records: Iterable[AuditRecord]) -> dict[str, int]:
    """Volume per action. What `cb audit --stats` prints."""
    tally: dict[str, int] = {}
    for entry in records:
        key = f"{entry.action}:{entry.outcome}"
        tally[key] = tally.get(key, 0) + 1
    return dict(sorted(tally.items()))
