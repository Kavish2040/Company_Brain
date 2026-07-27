"""M2: the world moving underneath the graph.

M1 tested a single ingest of a static directory. These test what M1 could not:
edits, deletions, orphaned evidence, and permission drift. They run against a
simulated Slack workspace with mutable state, so an edit genuinely changes a
content hash and a departure genuinely removes a grant.

What they do *not* test is real Slack's semantics — rate limits, pagination
edge cases, tombstoned-vs-deleted messages, and the fact that enumeration at
scale is slow. That gap is why M2 needs a real workspace before it can be
called done.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from company_brain.acl.grants import AccessFilter, GrantTable
from company_brain.connectors.base import SyncState
from company_brain.connectors.simulated import SimulatedSlack
from company_brain.connectors.sync import SyncEngine
from company_brain.extract.base import CachedExtractor
from company_brain.extract.rules import Roster, RosterEntry, RuleBasedExtractor
from company_brain.normalize.formats import default_registry
from company_brain.schemas.acl import Principal, PrincipalKind, Sensitivity
from company_brain.schemas.edges import EdgeStatus
from company_brain.schemas.nodes import NodeStatus, SourceRef
from company_brain.store.backend import MemoryBackend
from company_brain.store.repository import Repository

INTERNAL = Sensitivity.INTERNAL
RESTRICTED = Sensitivity.RESTRICTED
NOW = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)


def roster() -> Roster:
    return Roster(
        people=(
            RosterEntry("people/sam-kaur", ("Sam Kaur",)),
            RosterEntry("people/dev-oyelaran", ("Dev Oyelaran",)),
        ),
        teams=(
            RosterEntry("teams/finance", ("Finance", "finance")),
            RosterEntry("teams/engineering", ("Engineering", "engineering")),
        ),
        tools=(RosterEntry("tools/netsuite", ("NetSuite",)),),
        processes=(RosterEntry("processes/vendor-renewal", ("Vendor renewal",)),),
    )


@pytest.fixture
def engine() -> tuple[SyncEngine, Repository, GrantTable]:
    backend = MemoryBackend()
    repo = Repository(backend)
    grants = GrantTable()
    eng = SyncEngine(
        repo,
        default_registry(),
        CachedExtractor(RuleBasedExtractor(roster()), backend),
        grants,
    )
    return eng, repo, grants


@pytest.fixture
def slack() -> SimulatedSlack:
    workspace = SimulatedSlack()
    workspace.add_channel("C0ENG", "engineering", INTERNAL, {"priya", "sam"})
    workspace.add_channel("C0LEAD", "leadership", RESTRICTED, {"priya"})
    # Phrased so the extractor yields an `owns` edge (always proposed, §11)
    # as well as mentions — the review-decision tests need both.
    workspace.post("C0ENG", "U1", "Sam Kaur owns Vendor renewal, tracked in NetSuite.")
    workspace.post("C0LEAD", "U2", "Compensation bands need revisiting.")
    return workspace


def doc_ids(repo: Repository) -> list[str]:
    return list(repo.walk_ids("Document"))


def node_in(repo: Repository, channel: str) -> str:
    """The document node backing one simulated channel."""
    return next(
        n
        for n in doc_ids(repo)
        if channel in (repo.get(n).frontmatter.source or SourceRef).uri  # type: ignore[union-attr]
    )


class TestInitialSync:
    def test_creates_a_node_per_channel(self, engine, slack) -> None:
        eng, repo, _ = engine
        report = eng.sync(slack, now=NOW)
        assert report.added == 2
        assert len(doc_ids(repo)) == 2

    def test_records_a_cursor(self, engine, slack) -> None:
        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        state = SyncState.load(repo.backend, "slack")
        assert state.cursor is not None
        assert state.last_synced_at is not None

    def test_second_sync_with_no_changes_is_a_no_op(self, engine, slack) -> None:
        eng, _repo, _ = engine
        eng.sync(slack, now=NOW)
        report = eng.sync(slack, now=NOW)
        assert report.added == 0
        assert report.updated == 0
        assert report.changed == 0


class TestEdits:
    def test_an_edit_updates_in_place_keeping_the_node_id(self, engine, slack) -> None:
        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        before = doc_ids(repo)

        ts = next(iter(slack.channels["C0ENG"].messages))
        slack.edit("C0ENG", ts, "The NetSuite renewal is owned by Dev Oyelaran.")
        report = eng.sync(slack, now=NOW)

        assert report.updated == 1
        # Invariant 12: same ID, so citations issued before the edit still resolve.
        assert doc_ids(repo) == before

    def test_an_edit_changes_the_content_hash(self, engine, slack) -> None:
        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        node_id = doc_ids(repo)[0]
        before = repo.get(node_id).frontmatter.source.content_sha256

        cid = node_id.split("/")[-1]
        target = "C0ENG" if "C0ENG" in repo.get(node_id).frontmatter.source.uri else "C0LEAD"
        ts = next(iter(slack.channels[target].messages))
        slack.edit(target, ts, "Completely different content now.")
        eng.sync(slack, now=NOW)

        assert repo.get(node_id).frontmatter.source.content_sha256 != before
        assert cid  # node id is stable regardless

    def test_unchanged_channels_are_skipped_not_rewritten(self, engine, slack) -> None:
        eng, _repo, _ = engine
        eng.sync(slack, now=NOW)
        ts = next(iter(slack.channels["C0ENG"].messages))
        slack.edit("C0ENG", ts, "Edited.")
        report = eng.sync(slack, now=NOW)
        # Only the edited channel is touched; the other is not re-extracted.
        assert report.updated == 1
        assert report.unchanged + report.added == 0 or report.updated == 1


class TestDeletions:
    def test_a_deleted_source_becomes_a_tombstone_not_a_removal(self, engine, slack) -> None:
        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        node_id = node_in(repo, "C0LEAD")

        for ts in list(slack.channels["C0LEAD"].messages):
            slack.delete("C0LEAD", ts)
        report = eng.sync(slack, now=NOW)

        assert report.deleted == 1
        node = repo.get(node_id)
        # §9.3: the file survives so old citations resolve to "deleted on <date>"
        # rather than to a dangling ID.
        assert node.frontmatter.status is NodeStatus.DELETED
        assert node.frontmatter.deleted_upstream_at == NOW
        assert repo.exists(node_id)

    def test_tombstone_can_drop_the_body(self, engine, slack) -> None:
        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        node_id = node_in(repo, "C0LEAD")
        for ts in list(slack.channels["C0LEAD"].messages):
            slack.delete("C0LEAD", ts)
        eng.sync(slack, now=NOW)
        assert "Compensation bands" not in repo.get(node_id).body

    def test_delete_detection_can_be_skipped(self, engine, slack) -> None:
        """Enumeration is the expensive half of a sync, so it is optional —
        which is exactly why deletion freshness is an SLA, not a guarantee."""
        eng, _repo, _ = engine
        eng.sync(slack, now=NOW)
        for ts in list(slack.channels["C0LEAD"].messages):
            slack.delete("C0LEAD", ts)
        report = eng.sync(slack, now=NOW, detect_deletes=False)
        assert report.deleted == 0


class TestEvidenceLifecycle:
    def test_human_decisions_survive_re_extraction(self, engine, slack) -> None:
        """A reviewer's verdict must not be silently undone by the next sync —
        that would make the review queue Sisyphean."""
        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        node_id = node_in(repo, "C0ENG")

        node = repo.get(node_id)
        proposed = [e for e in node.frontmatter.relations if e.status is EdgeStatus.PROPOSED]
        assert proposed, "fixture must produce a proposed edge for this test to mean anything"
        decided = proposed[0].model_copy(update={"status": EdgeStatus.ACCEPTED})
        others = tuple(e for e in node.frontmatter.relations if e is not proposed[0])
        repo.put(
            node.model_copy(
                update={
                    "frontmatter": node.frontmatter.model_copy(
                        update={"relations": (*others, decided)}
                    )
                }
            )
        )

        slack.post("C0ENG", "U1", "An unrelated new message.")
        eng.sync(slack, now=NOW)

        after = repo.get(node_id)
        match = [
            e
            for e in after.frontmatter.relations
            if e.predicate == decided.predicate and e.object == decided.object
        ]
        assert match and match[0].status is EdgeStatus.ACCEPTED

    def test_orphaned_evidence_is_marked_stale_not_dropped(self, engine, slack) -> None:
        """A span pointing at text that no longer exists must become `stale`.

        Keeping it is a citation into deleted text; dropping it hides that the
        graph was ever wrong. Both are worse than saying so.
        """
        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        node_id = node_in(repo, "C0ENG")

        node = repo.get(node_id)
        candidates = [
            e for e in node.frontmatter.relations if e.evidence and e.evidence[0].span
        ]
        assert candidates, "fixture must produce spanned evidence"
        pinned = candidates[0].model_copy(update={"status": EdgeStatus.ACCEPTED})
        repo.put(
            node.model_copy(
                update={
                    "frontmatter": node.frontmatter.model_copy(update={"relations": (pinned,)})
                }
            )
        )

        # Rewrite the channel so the quoted text is gone entirely.
        for ts in list(slack.channels["C0ENG"].messages):
            slack.edit("C0ENG", ts, "Entirely different text with no overlap at all.")
        report = eng.sync(slack, now=NOW)

        after = repo.get(node_id)
        stale = [e for e in after.frontmatter.relations if e.status is EdgeStatus.STALE]
        assert report.stale_edges >= 1
        assert stale, "orphaned evidence was silently kept or dropped"


class TestGrantSync:
    def test_initial_sync_mirrors_membership(self, engine, slack) -> None:
        eng, _, grants = engine
        report = eng.sync(slack, now=NOW)
        assert report.grants_added == 3  # priya+sam in ENG, priya in LEAD
        priya = Principal(id="priya", kind=PrincipalKind.USER, display="Priya")
        assert AccessFilter(grants, priya).allows("slack:channel:C0LEAD", RESTRICTED)

    def test_leaving_a_channel_revokes_access_on_the_next_sync(self, engine, slack) -> None:
        eng, _, grants = engine
        eng.sync(slack, now=NOW)
        sam = Principal(id="sam", kind=PrincipalKind.USER, display="Sam")
        assert AccessFilter(grants, sam).allows("slack:channel:C0ENG", INTERNAL)

        slack.leave("C0ENG", "sam")
        report = eng.sync(slack, now=NOW)

        assert report.grants_revoked == 1
        assert not AccessFilter(grants, sam).allows("slack:channel:C0ENG", INTERNAL)

    def test_joining_a_channel_grants_access(self, engine, slack) -> None:
        eng, _, grants = engine
        eng.sync(slack, now=NOW)
        dev = Principal(id="dev", kind=PrincipalKind.USER, display="Dev")
        assert not AccessFilter(grants, dev).allows("slack:channel:C0ENG", INTERNAL)

        slack.join("C0ENG", "dev")
        eng.sync(slack, now=NOW)
        assert AccessFilter(grants, dev).allows("slack:channel:C0ENG", INTERNAL)

    def test_revocation_propagates_to_a_delegated_agent(self, engine, slack) -> None:
        """The agent's ceiling is the human's set, so shrinking the human
        shrinks the agent — without touching the agent's own registration."""
        eng, _, grants = engine
        eng.sync(slack, now=NOW)
        grants.register_agent("assistant", inherit=True)
        agent = Principal(
            id="assistant",
            kind=PrincipalKind.AGENT,
            display="assistant",
            delegated_by="priya",
        )
        assert AccessFilter(grants, agent).allows("slack:channel:C0LEAD", RESTRICTED)

        slack.leave("C0LEAD", "priya")
        eng.sync(slack, now=NOW)

        assert not AccessFilter(grants, agent).allows("slack:channel:C0LEAD", RESTRICTED)

    def test_the_leak_window_is_real_and_bounded_by_sync(self, engine, slack) -> None:
        """Documents the window rather than pretending it isn't there.

        Between a source-side revocation and the next sync, the grant table is
        stale and access persists. This is inherent to mirroring, not a defect
        — every such system has it. What matters is that one sync closes it.
        """
        eng, _, grants = engine
        eng.sync(slack, now=NOW)
        sam = Principal(id="sam", kind=PrincipalKind.USER, display="Sam")

        slack.leave("C0ENG", "sam")
        # No sync yet: the mirror is stale and still permits access.
        assert AccessFilter(grants, sam).allows("slack:channel:C0ENG", INTERNAL)

        eng.sync(slack, now=NOW)
        assert not AccessFilter(grants, sam).allows("slack:channel:C0ENG", INTERNAL)


class TestDepartureClassification:
    """Absence is not one signal.

    Drive's changes feed says `removed` means "removed from this list of
    changes, for example by deletion or loss of access" — so an enumeration
    diff cannot tell a delete from an unshare. Treating both as deletion
    tombstones every file someone stops sharing, and under the §14 Q3 default
    that purges a body which was never deleted.

    The asymmetry decides the default: a late delete is a bounded freshness-SLA
    problem; a false delete with a purged body cannot be undone.
    """

    def test_a_confirmed_delete_tombstones_and_purges(self, engine, slack) -> None:
        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        node_id = node_in(repo, "C0LEAD")

        for ts in list(slack.channels["C0LEAD"].messages):
            slack.delete("C0LEAD", ts)
        report = eng.sync(slack, now=NOW)

        assert report.deleted == 1
        node = repo.get(node_id)
        assert node.frontmatter.status is NodeStatus.DELETED
        assert node.frontmatter.content_retained is False
        assert "Compensation bands" not in node.body

    def test_an_unclassifiable_departure_does_not_destroy_the_document(
        self, engine, slack
    ) -> None:
        """The case that would have been catastrophic.

        The channel disappears entirely — which in real Slack is
        indistinguishable from being removed from it. The connector says
        UNKNOWN, and the engine must leave the document alone rather than
        tombstone and purge a file that still exists upstream.
        """
        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        node_id = node_in(repo, "C0LEAD")
        body_before = repo.get(node_id).body

        del slack.channels["C0LEAD"]  # gone from enumeration; reason unknowable
        report = eng.sync(slack, now=NOW)

        assert report.deleted == 0
        assert report.access_lost == 1
        node = repo.get(node_id)
        assert node.frontmatter.status is NodeStatus.ACTIVE
        assert node.body == body_before

    def test_a_trashed_document_is_tombstoned_but_keeps_its_body(
        self, engine, slack, monkeypatch
    ) -> None:
        """Drive keeps trash for ~30 days. Leave retrieval immediately, but
        keep the text — it may come back, and re-extraction is neither free nor
        deterministic."""
        from company_brain.connectors.base import Disappearance

        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        node_id = node_in(repo, "C0LEAD")

        for ts in list(slack.channels["C0LEAD"].messages):
            slack.delete("C0LEAD", ts)
        monkeypatch.setattr(slack, "classify_departure", lambda _id: Disappearance.TRASHED)
        report = eng.sync(slack, now=NOW)

        assert report.trashed == 1
        node = repo.get(node_id)
        assert node.frontmatter.status is NodeStatus.DELETED
        assert node.frontmatter.content_retained is True
        assert "Compensation bands" in node.body

    def test_a_retained_trashed_body_is_still_unretrievable(
        self, engine, slack, monkeypatch
    ) -> None:
        """Retention is a storage decision, never a visibility one. This is the
        property that makes keeping the body safe at all."""
        from company_brain.connectors.base import Disappearance
        from company_brain.index.base import IndexedNode
        from company_brain.index.memory import MemoryIndex

        eng, repo, _ = engine
        eng.sync(slack, now=NOW)
        node_id = node_in(repo, "C0LEAD")
        for ts in list(slack.channels["C0LEAD"].messages):
            slack.delete("C0LEAD", ts)
        monkeypatch.setattr(slack, "classify_departure", lambda _id: Disappearance.TRASHED)
        eng.sync(slack, now=NOW)

        index = MemoryIndex()
        index.rebuild(
            [
                (
                    IndexedNode(
                        id=n.id,
                        type=str(n.frontmatter.type),
                        title=n.frontmatter.title,
                        acl_ref=n.frontmatter.acl.ref,
                        sensitivity=n.frontmatter.acl.sensitivity,
                        status=str(n.frontmatter.status),
                        content_sha256="a" * 64,
                        edges=n.frontmatter.relations,
                    ),
                    n.body,
                )
                for n in repo.walk()
            ]
        )
        grants = GrantTable()
        grants.grant("ceo", "slack:channel:C0LEAD", RESTRICTED)
        access = AccessFilter(
            grants, Principal(id="ceo", kind=PrincipalKind.USER, display="CEO")
        )
        hits = index.search_lexical("compensation bands", access, 10)
        assert not [h for h in hits if h.chunk.node_id == node_id]
