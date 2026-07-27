"""Live editing rooms: the state, the merge rule, and nothing async.

One room per node. The room holds the authoritative body; the store holds the
truth. Between debounced flushes the two differ, and that gap is the whole
design — it is what buys "no save button" without a write per keystroke.

**The merge rule is last-write-wins, and it loses data.** Two people editing the
same paragraph within one round trip: the later write replaces the *entire*
body and the earlier typist's sentence is gone. There is no operational
transform and no CRDT here. Presence exists partly so that collision is
socially visible, and `EditOutcome.clobbered` exists so it is visible in the
logs rather than silent. docs/ARCHITECTURE.md §15 states the limit in full.

Everything in this module is synchronous and side-effect free apart from
`persist`. The async transport lives in `hub.py`, so the merge rule can be
tested without a socket.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Final

from company_brain.collab.guard import check_generated_regions
from company_brain.schemas.nodes import Node
from company_brain.store.repository import Repository

# Token *names*, not hex. DESIGN_SYSTEM §2 forbids raw hex in the UI, so the
# server names a palette slot and the client maps it to Tailwind classes.
PALETTE: Final[tuple[str, ...]] = ("amber", "cyan", "emerald", "fuchsia", "rose", "violet")


def participant_color(principal_id: str) -> str:
    """Stable colour for a principal, chosen without randomness.

    Invariant 3 bans `Math.random`-shaped non-determinism from output paths, and
    a caret that changes colour on reconnect reads as a second person in the
    room. Hashing the id fixes both.
    """
    digest = hashlib.blake2b(principal_id.encode("utf-8"), digest_size=4).digest()
    return PALETTE[int.from_bytes(digest, "big") % len(PALETTE)]


@dataclass(slots=True)
class Participant:
    """One open editor. Keyed by connection, not principal — the same person in
    two windows is two carets, and the demo depends on that being true."""

    connection: str
    principal: str
    display: str
    color: str
    anchor: int = 0
    head: int = 0

    def wire(self) -> dict[str, object]:
        return {
            "connection": self.connection,
            "principal": self.principal,
            "display": self.display,
            "color": self.color,
            "anchor": self.anchor,
            "head": self.head,
        }


@dataclass(slots=True)
class EditOutcome:
    revision: int
    body: str
    clobbered: bool
    """True when the author was editing an older revision. The write still won —
    that is what LWW means — but somebody's text was just overwritten."""


@dataclass(slots=True)
class RoomState:
    node_id: str
    body: str
    revision: int = 0
    dirty: bool = False
    participants: dict[str, Participant] = field(default_factory=dict)

    # ---- membership ----------------------------------------------------

    def join(self, connection: str, principal: str, display: str) -> Participant:
        participant = Participant(
            connection=connection,
            principal=principal,
            display=display,
            color=participant_color(principal),
        )
        self.participants[connection] = participant
        return participant

    def leave(self, connection: str) -> None:
        self.participants.pop(connection, None)

    @property
    def empty(self) -> bool:
        return not self.participants

    def presence(self) -> list[dict[str, object]]:
        """Sorted by connection id so the avatar stack doesn't reshuffle on
        every broadcast."""
        ordered = sorted(self.participants.values(), key=lambda p: p.connection)
        return [p.wire() for p in ordered]

    # ---- editing -------------------------------------------------------

    def apply_edit(self, connection: str, base_revision: int, body: str) -> EditOutcome:
        """Accept an edit under last-write-wins.

        Raises `FenceViolation` if the edit touched generated content, which is
        the one case where the write is refused outright: a human may edit
        around a fence, never inside one (invariant 13, inverted).
        """
        if connection not in self.participants:
            raise KeyError(f"connection {connection!r} is not in room {self.node_id!r}")

        check_generated_regions(self.body, body)

        clobbered = base_revision != self.revision
        self.body = body
        self.revision += 1
        self.dirty = True
        return EditOutcome(revision=self.revision, body=self.body, clobbered=clobbered)

    def move_cursor(self, connection: str, anchor: int, head: int) -> None:
        participant = self.participants.get(connection)
        if participant is None:
            return
        bound = len(self.body)
        participant.anchor = max(0, min(anchor, bound))
        participant.head = max(0, min(head, bound))


class SessionRegistry:
    """Every open room, in this process.

    In-process is a deliberate demo constraint: two uvicorn workers would each
    hold a different authoritative body for the same node, and the last flush
    would win at a granularity nobody could reason about. Single worker, or
    this needs a shared backplane (out of scope — see the plan).
    """

    def __init__(self, repo: Repository) -> None:
        self.repo = repo
        self._rooms: dict[str, RoomState] = {}

    def open(self, node_id: str) -> RoomState:
        """Get the live room, or seed a new one from the store."""
        room = self._rooms.get(node_id)
        if room is None:
            node = self.repo.get(node_id)
            room = RoomState(node_id=node_id, body=node.body)
            self._rooms[node_id] = room
        return room

    def find(self, node_id: str) -> RoomState | None:
        return self._rooms.get(node_id)

    def close_if_empty(self, node_id: str) -> bool:
        """Drop an unoccupied room so the next reader re-seeds from the store.

        Returns True if a room was actually dropped, which the caller uses to
        decide whether the index needs rebuilding.
        """
        room = self._rooms.get(node_id)
        if room is None or not room.empty:
            return False
        del self._rooms[node_id]
        return True

    def persist(self, node_id: str) -> bool:
        """Flush a dirty room to the markdown store. Returns True if it wrote.

        Goes through `Repository.put`, so the write is atomic (invariant 14) and
        the canonical emitter normalizes the body. Only `body` is carried over —
        frontmatter never comes from a client, so this path cannot widen an ACL
        (invariant 6) or move an ID (invariant 12).
        """
        room = self._rooms.get(node_id)
        if room is None or not room.dirty:
            return False

        current = self.repo.get(node_id)
        self.repo.put(Node(frontmatter=current.frontmatter, body=room.body))
        room.dirty = False
        return True
