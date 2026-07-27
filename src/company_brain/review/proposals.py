"""The proposal tree: what an agent wrote, and what a reviewer decides about it.

ARCHITECTURE §8.3 says an agent write lands in ``store/_proposals/<id>.md`` —
real markdown, diffable, reviewable in the same editor as everything else —
*plus* a ``review_queue`` row. This module is both halves.

The markdown file is the proposed node exactly as it would be written if
accepted, so "review the diff" and "read the file" are the same act. The queue
row is a JSON sidecar next to it: who proposed it, on whose behalf, what it
targets, and what the target looked like at the time. That is workflow state,
not graph content — the same category as ``store/_sync/`` — which is why it
carries wall-clock timestamps that invariant 4 keeps out of canonical files, and
why it is a sidecar rather than three more frontmatter fields on a node that has
to round-trip byte-identically.

Two properties worth stating, because both are load-bearing for the reviewer:

* **Proposal IDs are content-addressed.** The same agent proposing the same
  change twice produces one queue entry, not two. A queue that double-counts a
  retry is a queue whose depth means nothing.
* **A decided proposal is retained, never deleted.** Rejections are the only
  signal available for tuning the §11 gates, and a rejected proposal that
  vanishes takes the evidence of a miscalibrated gate with it.
"""

from __future__ import annotations

import difflib
import hashlib
import json
from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Final, Literal

from company_brain.schemas.acl import Sensitivity
from company_brain.schemas.edges import Edge
from company_brain.schemas.nodes import Node
from company_brain.store.repository import PROPOSALS_PREFIX, Repository
from company_brain.store.serialize import dump_node, parse_node

# Lines of unchanged text shown either side of a change. Enough to place the
# edit, few enough that a reviewer sees a diff rather than a document — the
# ROADMAP's 50-proposals-in-15-minutes budget is 18 seconds each.
DIFF_CONTEXT: Final = 2


def _now() -> datetime:
    return datetime.now(UTC)


class ProposalError(RuntimeError):
    """A proposal could not be stored, read, or applied."""


class StaleProposalError(ProposalError):
    """The target changed after the proposal was made.

    Accepting anyway would silently revert whatever happened in between, which
    is the one outcome a review step exists to prevent.
    """


class ProposalKind(StrEnum):
    NODE_BODY = "node_body"
    EDGE = "edge"


class ProposalState(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ProposalRecord:
    """The queue row. Never contains node content — only IDs and metadata."""

    proposal_id: str
    kind: ProposalKind
    target: str
    proposed_by: str
    delegated_by: str | None
    surface: str
    created_at: datetime
    # What the target's canonical bytes hashed to when the proposal was made.
    # The staleness check, and the reason accept cannot silently clobber.
    base_sha256: str
    sensitivity: Sensitivity
    state: ProposalState = ProposalState.PENDING
    decided_by: str | None = None
    decided_at: datetime | None = None
    # Set for edge proposals so the queue can group and filter by predicate
    # without parsing every proposal's frontmatter.
    predicate: str | None = None
    object: str | None = None
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "kind": str(self.kind),
            "target": self.target,
            "proposed_by": self.proposed_by,
            "delegated_by": self.delegated_by,
            "surface": self.surface,
            "created_at": _iso(self.created_at),
            "base_sha256": self.base_sha256,
            "sensitivity": str(self.sensitivity),
            "state": str(self.state),
            "decided_by": self.decided_by,
            "decided_at": _iso(self.decided_at) if self.decided_at else None,
            "predicate": self.predicate,
            "object": self.object,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> ProposalRecord:
        decided = raw.get("decided_at")
        return cls(
            proposal_id=str(raw["proposal_id"]),
            kind=ProposalKind(raw["kind"]),
            target=str(raw["target"]),
            proposed_by=str(raw["proposed_by"]),
            delegated_by=raw.get("delegated_by"),
            surface=str(raw.get("surface", "mcp")),
            created_at=_parse(str(raw["created_at"])),
            base_sha256=str(raw["base_sha256"]),
            sensitivity=Sensitivity(raw["sensitivity"]),
            state=ProposalState(raw.get("state", "pending")),
            decided_by=raw.get("decided_by"),
            decided_at=_parse(str(decided)) if decided else None,
            predicate=raw.get("predicate"),
            object=raw.get("object"),
            summary=str(raw.get("summary", "")),
        )


@dataclass(frozen=True, slots=True)
class LineChange:
    kind: Literal["context", "added", "removed", "gap"]
    text: str


@dataclass(frozen=True, slots=True)
class ProposalDiff:
    """What the reviewer actually looks at.

    Additions and removals are marked structurally rather than by colour —
    DESIGN_SYSTEM §6 asks for the alpha-fill idiom, not GitHub green/red, and a
    diff that is only legible in colour is not legible.
    """

    record: ProposalRecord
    target_title: str
    target_exists: bool
    stale: bool
    body: tuple[LineChange, ...]
    added_relations: tuple[Edge, ...]
    removed_relations: tuple[Edge, ...]

    @property
    def is_empty(self) -> bool:
        return not (self.body or self.added_relations or self.removed_relations)


def content_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def proposal_id(kind: ProposalKind, proposed_by: str, target: str, payload: str) -> str:
    """Content-addressed, so re-proposing the same change is idempotent.

    The agent's identity is part of the address: two agents independently
    reaching the same conclusion is corroboration, and collapsing them into one
    row would hide it.
    """
    digest = hashlib.blake2b(
        "\0".join((str(kind), proposed_by, target, payload)).encode("utf-8"),
        digest_size=8,
    ).hexdigest()
    return f"{kind}-{_slug(proposed_by)}-{digest}"


class ProposalStore:
    """Read and write ``store/_proposals/``.

    Writes go through here rather than through ``Repository.put_proposal``
    directly, because a proposal without its queue row is invisible to every
    reviewer — which is the failure mode that made the agent write path look
    finished while nothing could actually be reviewed.
    """

    def __init__(self, repo: Repository, *, clock: Callable[[], datetime] = _now) -> None:
        self.repo = repo
        self._clock = clock

    # ---- write ---------------------------------------------------------

    def put(self, record: ProposalRecord, node: Node) -> ProposalRecord:
        """Store a proposal and its queue row.

        Re-proposing an identical change preserves the original ``created_at``
        so the queue's age ordering reflects when the claim was first made, not
        when an agent last retried.
        """
        existing = self._read_record(record.proposal_id)
        if existing is not None:
            record = replace(record, created_at=existing.created_at)
        self.repo.put_proposal(record.proposal_id, node)
        self._write_record(record)
        return record

    def decide(
        self, proposal_id_: str, state: ProposalState, *, reviewer: str
    ) -> ProposalRecord:
        """Record a human decision. Retained, never deleted."""
        record = self.get_record(proposal_id_)
        if record.state is not ProposalState.PENDING:
            raise ProposalError(f"{proposal_id_} is already {record.state}")
        decided = replace(
            record, state=state, decided_by=reviewer, decided_at=self._clock().astimezone(UTC)
        )
        self._write_record(decided)
        return decided

    def reopen(self, proposal_id_: str, *, reviewer: str) -> ProposalRecord:
        """Undo a rejection. An acceptance is not undoable here, and says so.

        The asymmetry is real rather than an omission: rejecting a proposal
        changes only its queue row, so putting the row back is a complete undo.
        Accepting it wrote to the graph, and "un-writing" a node is not an undo,
        it is a second write that a reviewer has to see. So the honest answer is
        to refuse and point at the edge the acceptance created.
        """
        record = self.get_record(proposal_id_)
        if record.state is ProposalState.ACCEPTED:
            raise ProposalError(
                f"{proposal_id_} is already in the graph; reject the edge it created "
                f"on {record.target} rather than reopening the proposal"
            )
        if record.state is ProposalState.PENDING:
            raise ProposalError(f"{proposal_id_} is already pending")
        reopened = replace(
            record,
            state=ProposalState.PENDING,
            decided_by=reviewer,
            decided_at=self._clock().astimezone(UTC),
        )
        self._write_record(reopened)
        return reopened

    def apply(self, proposal_id_: str, *, reviewer: str) -> Node:
        """Write an accepted proposal into the graph.

        The only path from a proposal to the canonical store, and it runs under
        a human's identity by construction — ``reviewer`` has no default.

        **An edge proposal is rebased, not replayed.** Ten agent proposals
        against one document is the normal case, and accepting the first one
        moves the document — so replaying the second one's whole node would drop
        the first one's edge and stall the queue on its own success. What the
        proposal actually claims is one relation, so that relation is applied to
        the node *as it stands now*, and the reviewer's eight remaining accepts
        keep working.

        **A body proposal is not**, and staleness there is fatal. Rebasing prose
        means a three-way merge, and a merge nobody reviewed is exactly the
        silent revert the review step exists to prevent. The reviewer is told to
        re-propose, which is the honest answer.

        ``input_tiers`` carries the proposal's inherited sensitivity into
        ``Repository.put``, so invariant 6 is re-checked at the writer even
        though the MCP layer already refused to create a widening proposal. Two
        checks, because the second one is the one that holds when a third
        surface starts producing proposals.
        """
        record = self.get_record(proposal_id_)
        proposed = self.get_node(proposal_id_)
        current = self.repo.find(record.target)
        if current is None:
            raise ProposalError(f"{record.target} no longer exists; {proposal_id_} is moot")

        moved = content_sha256(dump_node(current)) != record.base_sha256
        if record.kind is ProposalKind.EDGE:
            node = self._rebase_edge(record, proposed, current)
        else:
            if moved:
                raise StaleProposalError(
                    f"{proposal_id_} was made against an older revision of "
                    f"{record.target}; re-propose it against the current one"
                )
            node = proposed

        self.repo.put(node, input_tiers=(record.sensitivity,))
        self.decide(proposal_id_, ProposalState.ACCEPTED, reviewer=reviewer)
        return node

    def _rebase_edge(self, record: ProposalRecord, proposed: Node, current: Node) -> Node:
        """Apply the one relation this proposal claims onto the current node.

        Matched by ``(predicate, object)`` from the queue row rather than by
        diffing the two relation sets: a set difference would also resurrect any
        edge the node has *lost* since the proposal was made, including one a
        reviewer just rejected.
        """
        edge = next(
            (
                e
                for e in proposed.frontmatter.relations
                if str(e.predicate) == record.predicate and e.object == record.object
            ),
            None,
        )
        if edge is None:
            raise ProposalError(
                f"{record.proposal_id} names {record.predicate} -> {record.object}, "
                f"which is not in its own markdown"
            )
        merged = {e.sort_key(): e for e in current.frontmatter.relations}
        merged[edge.sort_key()] = edge
        return Node(
            frontmatter=current.frontmatter.model_copy(
                update={"relations": tuple(merged.values())}
            ),
            body=current.body,
        )

    # ---- read ----------------------------------------------------------

    def get_record(self, proposal_id_: str) -> ProposalRecord:
        record = self._read_record(proposal_id_)
        if record is None:
            raise ProposalError(f"no proposal {proposal_id_!r}")
        return record

    def get_node(self, proposal_id_: str) -> Node:
        text = self.repo.backend.read_text(f"{PROPOSALS_PREFIX}/{proposal_id_}.md")
        if text is None:
            raise ProposalError(f"proposal {proposal_id_!r} has no markdown")
        return parse_node(text)

    def records(
        self, *, state: ProposalState | None = ProposalState.PENDING
    ) -> list[ProposalRecord]:
        """Queue rows, oldest first — the order a reviewer should work them in."""
        out = [r for r in self._scan() if state is None or r.state is state]
        out.sort(key=lambda r: (r.created_at, r.proposal_id))
        return out

    def diff(self, proposal_id_: str) -> ProposalDiff:
        """What accepting this proposal would do to the node as it stands now.

        Computed against *current*, not against the proposal's base, so it shows
        the reviewer the change they are actually approving rather than the one
        the agent originally described.
        """
        record = self.get_record(proposal_id_)
        proposed = self.get_node(proposal_id_)
        current = self.repo.find(record.target)

        before_edges = current.frontmatter.relations if current is not None else ()
        after_edges = proposed.frontmatter.relations
        before_keys = {e.sort_key() for e in before_edges}
        after_keys = {e.sort_key() for e in after_edges}

        is_edge = record.kind is ProposalKind.EDGE
        moved = current is not None and content_sha256(dump_node(current)) != record.base_sha256

        return ProposalDiff(
            record=record,
            target_title=(current.frontmatter.title if current is not None else record.target),
            target_exists=current is not None,
            # `stale` means "this can no longer be applied", not "the node
            # moved". An edge proposal rebases, so a moved node is not its
            # problem; a body proposal cannot, so it is.
            stale=moved and not is_edge,
            # An edge proposal never touches the body, and after a rebase it
            # keeps whatever body the node has now — so showing a body diff here
            # would be showing the reviewer somebody else's change.
            body=()
            if is_edge
            else tuple(body_diff(current.body if current else "", proposed.body)),
            added_relations=tuple(e for e in after_edges if e.sort_key() not in before_keys),
            # Only a body proposal can drop a relation; for an edge proposal a
            # missing relation means the node gained one elsewhere, which the
            # rebase keeps.
            removed_relations=(
                ()
                if is_edge
                else tuple(e for e in before_edges if e.sort_key() not in after_keys)
            ),
        )

    def accept_rate(self) -> dict[str, tuple[int, int]]:
        """Per-kind (accepted, decided) counts for agent proposals.

        The same calibration question §11 asks of the extraction gates, asked of
        the agent write path: near 100% and review is a rubber stamp, near 10%
        and the agent is generating work rather than doing it.
        """
        tally: dict[str, list[int]] = {}
        for record in self._scan():
            if record.state is ProposalState.PENDING:
                continue
            key = record.predicate or str(record.kind)
            bucket = tally.setdefault(key, [0, 0])
            bucket[1] += 1
            if record.state is ProposalState.ACCEPTED:
                bucket[0] += 1
        return {k: (v[0], v[1]) for k, v in sorted(tally.items())}

    # ---- internals -----------------------------------------------------

    def _scan(self) -> Iterator[ProposalRecord]:
        for path in self.repo.backend.walk(PROPOSALS_PREFIX):
            if not path.endswith(".json"):
                continue
            text = self.repo.backend.read_text(path)
            if text is None:
                continue
            try:
                yield ProposalRecord.from_dict(json.loads(text))
            except (ValueError, KeyError) as exc:
                raise ProposalError(f"corrupt queue row at {path}: {exc}") from exc

    def _row_path(self, proposal_id_: str) -> str:
        return f"{PROPOSALS_PREFIX}/{proposal_id_}.json"

    def _read_record(self, proposal_id_: str) -> ProposalRecord | None:
        text = self.repo.backend.read_text(self._row_path(proposal_id_))
        if text is None:
            return None
        return ProposalRecord.from_dict(json.loads(text))

    def _write_record(self, record: ProposalRecord) -> None:
        self.repo.backend.write_text(
            self._row_path(record.proposal_id),
            json.dumps(record.to_dict(), indent=2, sort_keys=True) + "\n",
        )


def body_diff(before: str, after: str, *, context: int = DIFF_CONTEXT) -> list[LineChange]:
    """Line diff with bounded context, or an empty list when nothing changed.

    ``difflib`` rather than a word-level diff: node bodies are prose and lists,
    the reviewer's question is "what did it add", and a line diff answers that
    without the false precision of intra-line highlighting on reflowed text.
    """
    if before == after:
        return []
    old = before.splitlines()
    new = after.splitlines()

    out: list[LineChange] = []
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            block = old[i1:i2]
            if len(block) <= context * 2:
                out.extend(LineChange("context", line) for line in block)
                continue
            out.extend(LineChange("context", line) for line in block[:context])
            out.append(LineChange("gap", f"… {len(block) - context * 2} unchanged lines"))
            out.extend(LineChange("context", line) for line in block[-context:])
            continue
        if tag in ("replace", "delete"):
            out.extend(LineChange("removed", line) for line in old[i1:i2])
        if tag in ("replace", "insert"):
            out.extend(LineChange("added", line) for line in new[j1:j2])

    # A leading or trailing all-context run is padding around nothing.
    while out and out[0].kind in ("context", "gap"):
        out.pop(0)
    while out and out[-1].kind in ("context", "gap"):
        out.pop()
    return out


def _slug(value: str) -> str:
    return "".join(c if c.isalnum() or c == "-" else "-" for c in value.lower())[:40]


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
