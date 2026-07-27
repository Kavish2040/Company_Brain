"""The live-editing merge rule, and the guard that keeps it inside its lane.

Two things are worth testing here and they pull in opposite directions:

* Last-write-wins really does overwrite. The tests assert the data loss rather
  than papering over it, because a future reader who "fixes" this into a merge
  has changed the contract and should have to change a test to do it.
* A human edit may never reach generated content. That one is not best-effort.
"""

from __future__ import annotations

import pytest

from company_brain.collab.guard import FenceViolation, check_generated_regions
from company_brain.collab.session import (
    PALETTE,
    RoomState,
    SessionRegistry,
    participant_color,
)
from company_brain.schemas.acl import AclRef, Sensitivity
from company_brain.schemas.nodes import Frontmatter, Node, NodeType
from company_brain.store.backend import MemoryBackend
from company_brain.store.fences import render_fence, upsert_region
from company_brain.store.repository import Repository

NODE_ID = "processes/vendor-renewal"


def make_node(body: str = "Human prose.") -> Node:
    return Node(
        frontmatter=Frontmatter(
            id=NODE_ID,
            type=NodeType.PROCESS,
            title="Vendor renewal",
            acl=AclRef(ref="fs:corpus:docs", sensitivity=Sensitivity.INTERNAL),
        ),
        body=body,
    )


@pytest.fixture
def repo() -> Repository:
    repository = Repository(MemoryBackend())
    repository.put(make_node())
    return repository


class TestGuard:
    def test_editing_around_a_fence_is_allowed(self) -> None:
        stored = upsert_region("Intro.", "mentions", "Mentioned in 3 documents.")
        edited = "A new paragraph.\n\n" + stored
        check_generated_regions(stored, edited)  # must not raise

    def test_editing_inside_a_fence_is_refused(self) -> None:
        stored = upsert_region("Intro.", "mentions", "Mentioned in 3 documents.")
        tampered = stored.replace("Mentioned in 3 documents.", "Mentioned in 900 documents.")
        with pytest.raises(FenceViolation, match="interior of generated region"):
            check_generated_regions(stored, tampered)

    def test_deleting_a_fence_is_refused(self) -> None:
        stored = upsert_region("Intro.", "mentions", "Mentioned in 3 documents.")
        with pytest.raises(FenceViolation, match="added or removed"):
            check_generated_regions(stored, "Intro.")

    def test_rewriting_the_recorded_hash_is_refused(self) -> None:
        """The hash is what makes tampering detectable at all, so forging it has
        to fail on its own — not merely because the interior also changed."""
        stored = upsert_region("Intro.", "mentions", "Mentioned in 3 documents.")
        forged = stored.replace("hash=", "hash=0", 1)
        with pytest.raises(FenceViolation):
            check_generated_regions(stored, forged)

    def test_renaming_a_region_is_refused(self) -> None:
        stored = render_fence("mentions", "Mentioned in 3 documents.")
        renamed = stored.replace("region=mentions", "region=owners")
        with pytest.raises(FenceViolation, match="reordered or renamed"):
            check_generated_regions(stored, renamed)


class TestLastWriteWins:
    def test_edit_bumps_revision_and_broadcasts_body(self) -> None:
        room = RoomState(node_id=NODE_ID, body="one")
        room.join("c1", "ceo", "Chief Executive")

        outcome = room.apply_edit("c1", 0, "two")

        assert (outcome.revision, outcome.body) == (1, "two")
        assert not outcome.clobbered
        assert room.dirty

    def test_a_stale_write_still_wins_and_says_so(self) -> None:
        """The documented failure. Editing from an old revision overwrites the
        newer text; `clobbered` is how that becomes visible instead of silent."""
        room = RoomState(node_id=NODE_ID, body="")
        room.join("c1", "ceo", "Chief Executive")
        room.join("c2", "eng-ic", "Sam Kelly")

        room.apply_edit("c1", 0, "written by the first person")
        outcome = room.apply_edit("c2", 0, "written by the second person")

        assert outcome.clobbered
        assert room.body == "written by the second person"

    def test_an_unknown_connection_cannot_edit(self) -> None:
        room = RoomState(node_id=NODE_ID, body="one")
        with pytest.raises(KeyError):
            room.apply_edit("ghost", 0, "two")

    def test_fence_violation_leaves_the_room_untouched(self) -> None:
        stored = upsert_region("Intro.", "mentions", "Mentioned in 3 documents.")
        room = RoomState(node_id=NODE_ID, body=stored)
        room.join("c1", "ceo", "Chief Executive")

        with pytest.raises(FenceViolation):
            room.apply_edit("c1", 0, stored.replace("3 documents", "900 documents"))

        assert room.body == stored
        assert room.revision == 0
        assert not room.dirty


class TestPresence:
    def test_colour_is_stable_and_in_the_palette(self) -> None:
        assert participant_color("ceo") == participant_color("ceo")
        assert participant_color("ceo") in PALETTE

    def test_the_same_person_in_two_windows_is_two_carets(self) -> None:
        room = RoomState(node_id=NODE_ID, body="")
        room.join("c1", "ceo", "Chief Executive")
        room.join("c2", "ceo", "Chief Executive")
        assert len(room.presence()) == 2

    def test_cursors_are_clamped_to_the_body(self) -> None:
        room = RoomState(node_id=NODE_ID, body="12345")
        room.join("c1", "ceo", "Chief Executive")
        room.move_cursor("c1", -10, 999)
        participant = room.participants["c1"]
        assert (participant.anchor, participant.head) == (0, 5)


class TestPersistence:
    def test_persist_writes_the_body_and_clears_the_flag(self, repo: Repository) -> None:
        registry = SessionRegistry(repo)
        room = registry.open(NODE_ID)
        room.join("c1", "ceo", "Chief Executive")
        room.apply_edit("c1", 0, "Edited live.")

        assert registry.persist(NODE_ID) is True
        assert repo.get(NODE_ID).body == "Edited live."
        assert registry.persist(NODE_ID) is False, "a clean room must not rewrite the file"

    def test_persist_preserves_frontmatter(self, repo: Repository) -> None:
        """A client sends a body and nothing else, so an ACL cannot widen
        (invariant 6) and an ID cannot move (invariant 12) through this path."""
        registry = SessionRegistry(repo)
        room = registry.open(NODE_ID)
        room.join("c1", "ceo", "Chief Executive")
        room.apply_edit("c1", 0, "Edited live.")
        registry.persist(NODE_ID)

        assert repo.get(NODE_ID).frontmatter == make_node().frontmatter

    def test_a_room_reseeds_from_the_store_after_everyone_leaves(
        self, repo: Repository
    ) -> None:
        registry = SessionRegistry(repo)
        room = registry.open(NODE_ID)
        room.join("c1", "ceo", "Chief Executive")
        room.apply_edit("c1", 0, "Edited live.")
        registry.persist(NODE_ID)
        room.leave("c1")

        assert registry.close_if_empty(NODE_ID) is True
        assert registry.open(NODE_ID).body == "Edited live."

    def test_an_occupied_room_is_never_dropped(self, repo: Repository) -> None:
        registry = SessionRegistry(repo)
        registry.open(NODE_ID).join("c1", "ceo", "Chief Executive")
        assert registry.close_if_empty(NODE_ID) is False
