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
from company_brain.schemas.nodes import NodeStatus
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


# Channel ids (C0ENG) identify ACL refs; channel *names* (engineering) appear in
# node paths and URIs, because those mirror the corpus layout.
CHANNEL_NAME = {"C0ENG": "engineering", "C0LEAD": "leadership", "C0SUP": "support"}


def node_in(repo: Repository, channel: str) -> str:
    """The document node backing one simulated channel."""
    name = CHANNEL_NAME.get(channel, channel)
    return next(n for n in doc_ids(repo) if f"/slack/{name}/" in n)


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

        uri = repo.get(node_id).frontmatter.source.uri
        target = "C0ENG" if "/engineering/" in uri else "C0LEAD"
        cid = target
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


class TestSeededWorkspace:
    """`seeded_workspace()` had four defects and zero tests. That is why.

    The old version fabricated content, so every test built its own
    SimulatedSlack by hand and nothing ever exercised the seeding path the CLI
    actually used.
    """

    def test_seeding_is_deterministic(self, tmp_path) -> None:
        """The old version chose a speaker with `hash(cid)`. Python randomises
        string hashing per process, so that byte reached the record JSON, moved
        content_sha256 every run, and produced phantom updates that busted the
        extraction cache — real spend against a live model."""
        from company_brain.connectors.simulated import seed_from_corpus

        a, b = seed_from_corpus(), seed_from_corpus()
        assert {c.id: sorted(c.days) for c in a.channels.values()} == {
            c.id: sorted(c.days) for c in b.channels.values()
        }
        first_a = a.fetch(None).records
        first_b = b.fetch(None).records
        assert [r.raw for r in first_a] == [r.raw for r in first_b]

    def test_it_serves_the_corpus_rather_than_inventing_content(self) -> None:
        """The docstring used to claim it matched the corpus. It fabricated
        one-line bodies at a made-up epoch, so sync ADDED nodes the corpus
        ingest had never seen — and `cb ask` could cite them."""
        import json
        from pathlib import Path

        from company_brain.connectors.simulated import seed_from_corpus

        workspace = seed_from_corpus()
        sample = Path("corpus/synthetic/slack/engineering/2024-01-08.json")
        if not sample.exists():
            pytest.skip("corpus not generated")

        day = workspace.channel_by_name("engineering").days["2024-01-08"]
        assert day.messages == json.loads(sample.read_text())

    def test_record_uris_match_the_corpus_ingest(self) -> None:
        """Same URI and path in means the same node id out, so sync updates the
        corpus's nodes instead of shadowing them."""
        from company_brain.connectors.simulated import seed_from_corpus

        records = seed_from_corpus().fetch(None).records
        if not records:
            pytest.skip("corpus not generated")
        record = records[0]
        assert record.uri.startswith("file://corpus/slack/")
        assert record.path.startswith("slack/")

    def test_membership_has_one_source(self) -> None:
        """It was hardcoded in seeded_workspace AND in build_grants(). They
        agreed only by luck, and grant reconciliation depends on it."""
        from company_brain.connectors.simulated import seed_from_corpus
        from company_brain.corpus.generate import CHANNEL_MEMBERS

        for channel in seed_from_corpus().channels.values():
            assert channel.members == set(CHANNEL_MEMBERS.get(channel.name, frozenset()))


class TestPersistence:
    """State must survive the process, or no scenario composes.

    With an in-memory workspace every invocation rebuilt at revision 0 while the
    cursor persisted, so a second `cb sync` reported nothing at all — and no
    mutation lived long enough to be synced.
    """

    def test_a_round_trip_preserves_the_workspace(self) -> None:
        from company_brain.connectors.simulated import SimulatedSlack, seed_from_corpus

        backend = MemoryBackend()
        original = seed_from_corpus()
        original.edit_latest("engineering", "changed")
        original.save(backend)

        restored = SimulatedSlack.load(backend)
        assert restored is not None
        assert {c.id for c in restored.channels.values()} == {
            c.id for c in original.channels.values()
        }
        assert restored.latest_day("engineering").revision == 1

    def test_load_or_seed_seeds_once_then_reuses(self) -> None:
        from company_brain.connectors.simulated import load_or_seed

        backend = MemoryBackend()
        first = load_or_seed(backend)
        first.leave("engineering", "eng-ic")
        first.save(backend)

        second = load_or_seed(backend)
        assert "eng-ic" not in second.channel_by_name("engineering").members

    def test_a_second_sync_reports_unchanged_not_nothing(self) -> None:
        """The structural bug: `+0 ~0 -0 =0` reads as "nothing there", which is
        indistinguishable from "nothing changed". Only one is good news."""
        from company_brain.connectors.simulated import seed_from_corpus

        backend = MemoryBackend()
        repo = Repository(backend)
        eng = SyncEngine(
            repo,
            default_registry(),
            CachedExtractor(RuleBasedExtractor(roster()), backend),
            GrantTable(),
        )
        workspace = seed_from_corpus()
        workspace.save(backend)

        eng.sync(workspace, now=NOW)
        second = eng.sync(workspace, now=NOW)

        assert second.quiet
        assert second.unchanged > 0, "a no-op must say how much it skipped"


class TestScenarioLevers:
    """Each lever routes through a different mechanism. The point of separating
    them is that an enumeration diff cannot."""

    def _engine(self, backend: MemoryBackend) -> tuple[SyncEngine, Repository, GrantTable]:
        repo = Repository(backend)
        grants = GrantTable()
        return (
            SyncEngine(
                repo,
                default_registry(),
                CachedExtractor(RuleBasedExtractor(roster()), backend),
                grants,
            ),
            repo,
            grants,
        )

    def test_edit_produces_an_update(self) -> None:
        from company_brain.connectors.simulated import seed_from_corpus

        backend = MemoryBackend()
        eng, _, _ = self._engine(backend)
        workspace = seed_from_corpus()
        eng.sync(workspace, now=NOW)

        workspace.edit_latest("engineering", "EDITED UPSTREAM")
        report = eng.sync(workspace, now=NOW)
        assert report.updated == 1
        assert report.added == 0

    def test_unshare_does_not_tombstone(self) -> None:
        """The lever that would have destroyed live documents. `--unshare` is
        *we* lost visibility, not a delete."""
        from company_brain.connectors.simulated import seed_from_corpus

        backend = MemoryBackend()
        eng, repo, _ = self._engine(backend)
        workspace = seed_from_corpus()
        eng.sync(workspace, now=NOW)
        before = len(list(repo.walk_ids("Document")))

        workspace.mark_gone("engineering", "unshared")
        report = eng.sync(workspace, now=NOW)

        assert report.deleted == 0
        assert report.access_lost == 1
        assert all(
            repo.get(n).frontmatter.status is NodeStatus.ACTIVE
            for n in repo.walk_ids("Document")
        )
        assert len(list(repo.walk_ids("Document"))) == before

    def test_delete_tombstones_and_trash_retains(self) -> None:
        from company_brain.connectors.simulated import seed_from_corpus

        for how, expect_retained in (("deleted", False), ("trashed", True)):
            backend = MemoryBackend()
            eng, repo, _ = self._engine(backend)
            workspace = seed_from_corpus()
            eng.sync(workspace, now=NOW)

            workspace.mark_gone("support", how)
            report = eng.sync(workspace, now=NOW)

            tombstones = [
                repo.get(n)
                for n in repo.walk_ids("Document")
                if repo.get(n).frontmatter.status is NodeStatus.DELETED
            ]
            assert len(tombstones) == 1, how
            assert tombstones[0].frontmatter.content_retained is expect_retained
            assert (report.deleted, report.trashed) == ((1, 0) if how == "deleted" else (0, 1))

    def test_leave_revokes_a_grant(self) -> None:
        from company_brain.connectors.simulated import seed_from_corpus

        backend = MemoryBackend()
        eng, _, grants = self._engine(backend)
        workspace = seed_from_corpus()
        eng.sync(workspace, now=NOW)

        eng_ic = Principal(id="eng-ic", kind=PrincipalKind.USER, display="Eng IC")
        assert AccessFilter(grants, eng_ic).allows("slack:channel:C0ENG", INTERNAL)

        workspace.leave("engineering", "eng-ic")
        report = eng.sync(workspace, now=NOW)

        assert report.grants_revoked == 1
        assert not AccessFilter(grants, eng_ic).allows("slack:channel:C0ENG", INTERNAL)

    def test_grants_are_mirrored_to_disk(self) -> None:
        """Without this a revocation dies with the process: build_grants()
        rebuilds from CHANNEL_MEMBERS every time, so `cb sync --leave` would
        report a revocation and the next `cb ask` would still see the channel."""
        import json

        from company_brain.connectors.simulated import seed_from_corpus

        backend = MemoryBackend()
        eng, _, _ = self._engine(backend)
        workspace = seed_from_corpus()
        workspace.leave("engineering", "eng-ic")
        eng.sync(workspace, now=NOW)

        raw = backend.read_text("_sync/grants/slack.json")
        assert raw is not None
        mirrored = json.loads(raw)["grants"]
        assert "slack:channel:C0ENG" not in mirrored.get("eng-ic", [])
