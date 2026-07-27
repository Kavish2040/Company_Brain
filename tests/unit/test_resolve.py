"""Entity resolution layer 3 (ARCHITECTURE §10).

The acceptance module proves the merge round-trips. These prove the parts that
would let a *wrong* merge get proposed in the first place — which is where the
damage in an entity-resolution system actually comes from. §10.2 lists six ways
this fails; the ones layer 3 can defend against have a test here, and the ones
it cannot are flagged in `resolve/__init__.py` rather than papered over.

Determinism gets its own class. Blocking, scoring and proposal ordering all sit
on top of set and dict operations, so "it happened to be sorted this run" is a
real failure mode; the last test runs the whole pipeline in two subprocesses
under different `PYTHONHASHSEED` values, which is the only way to catch a
`hash()` leak from inside one process.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from datetime import UTC, datetime
from pathlib import Path

import pytest

from company_brain.resolve import (
    EntityProfile,
    Layer3Resolver,
    MergeError,
    Merger,
    Policy,
    ReviewWorkflow,
    SameAsProposalStore,
    block,
    blocking_keys,
    identity_conflict,
    score_pair,
)
from company_brain.resolve.proposals import DECISION_REGION, SameAsProposalError
from company_brain.review.queue import Decision, PendingEdge
from company_brain.schemas.acl import AclRef, Sensitivity
from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance
from company_brain.schemas.nodes import Frontmatter, Node, NodeStatus, NodeType
from company_brain.store.backend import MemoryBackend
from company_brain.store.repository import Repository

INTERNAL = Sensitivity.INTERNAL
JAN = datetime(2024, 1, 8, 9, 0, tzinfo=UTC)


def profile(
    node_id: str,
    title: str,
    *,
    aliases: tuple[str, ...] = (),
    node_type: NodeType = NodeType.PERSON,
    documents: tuple[str, ...] = (),
    channels: tuple[str, ...] = (),
    neighbours: tuple[str, ...] = (),
    seen: tuple[datetime, datetime] | None = None,
) -> EntityProfile:
    from company_brain.resolve import identity_keys

    return EntityProfile(
        node_id=node_id,
        node_type=node_type,
        title=title,
        aliases=tuple(sorted(aliases)),
        identity_keys=identity_keys((title, *aliases)),
        mentioned_in=documents,
        channels=channels,
        neighbours=neighbours,
        first_seen=seen[0] if seen else None,
        last_seen=seen[1] if seen else None,
    )


def entity(
    repo: Repository,
    node_id: str,
    title: str,
    *,
    aliases: tuple[str, ...] = (),
    node_type: NodeType = NodeType.PERSON,
    body: str = "",
    relations: tuple[Edge, ...] = (),
) -> Node:
    node = Node(
        frontmatter=Frontmatter(
            id=node_id,
            type=node_type,
            title=title,
            acl=AclRef(ref="fs:corpus:docs", sensitivity=INTERNAL),
            aliases=aliases,
            relations=relations,
        ),
        body=body,
    )
    repo.put(node)
    return node


@pytest.fixture()
def repo() -> Repository:
    return Repository(MemoryBackend())


class TestBlocking:
    """Candidate generation must be sub-quadratic and must say what it skipped."""

    def test_only_entities_sharing_a_key_are_compared(self) -> None:
        people = tuple(
            profile(f"people/p{i}", f"Person{i} Surname{i}", aliases=(f"p{i}@co.example",))
            for i in range(60)
        )
        result = block(people)
        assert result.exhaustive_comparisons == 60 * 59 // 2
        assert result.comparisons == 0, "entities with nothing in common were compared"

    def test_a_shared_surname_produces_exactly_one_pair(self) -> None:
        result = block(
            (
                profile("people/priya-raman", "Priya Raman"),
                profile("people/arjun-raman", "Arjun Raman"),
                profile("people/mei-tanaka", "Mei Tanaka"),
            )
        )
        assert [(p.left, p.right) for p in result.pairs] == [
            ("people/arjun-raman", "people/priya-raman")
        ]
        assert [str(k) for k in result.pairs[0].keys] == ["surname:raman"]

    def test_an_oversized_block_is_dropped_and_reported(self) -> None:
        crowd = tuple(profile(f"people/x{i}", f"Given{i} Smith") for i in range(50))
        result = block(crowd, max_block_size=40)
        assert result.comparisons == 0
        assert ("surname:smith", 50) in [(str(k), n) for k, n in result.oversized]
        # A dropped block that nobody hears about reads downstream as "compared,
        # found nothing" — the opposite of what happened.
        assert "NOT compared" in _summary_of(result)

    def test_different_types_never_pair(self) -> None:
        """§10.2's Snowflake case: same string, different kind of thing."""
        result = block(
            (
                profile("tools/snowflake", "Snowflake", node_type=NodeType.TOOL),
                profile("teams/snowflake", "Snowflake", node_type=NodeType.TEAM),
            )
        )
        assert result.comparisons == 0

    def test_a_bare_initial_is_not_a_blocking_key(self) -> None:
        """ "Sam K." is the string §10.2 says must stay ambiguous. It buys no
        bucket, so it can never pull two people together on its own."""
        keys = blocking_keys(profile("people/sam", "Sam K."))
        assert keys == ()

    def test_an_alias_can_supply_the_key_the_title_lacks(self) -> None:
        result = block(
            (
                profile("people/sk", "SK", aliases=("Samantha Kaur",)),
                profile("people/sam-kaur", "Sam Kaur"),
            )
        )
        assert result.comparisons == 1
        assert "surname:kaur" in {str(k) for k in result.pairs[0].keys}


def _summary_of(blocking: object) -> str:
    from company_brain.resolve.resolver import ResolutionReport

    assert hasattr(blocking, "oversized")
    return ResolutionReport(
        proposals=(), considered=(), blocking=blocking, deferred=()
    ).summary()


class TestTheTwoPeopleOneNameFailure:
    """§10.2's headline failure, and why co-occurrence cannot be trusted to fix it."""

    def test_distinct_directory_accounts_veto_the_match(self) -> None:
        left = profile("people/priya-raman", "Priya Raman", aliases=("priya@meridian.example",))
        right = profile(
            "people/arjun-raman", "Arjun Raman", aliases=("arjun@meridian.example",)
        )
        reason = identity_conflict(left.surfaces, right.surfaces)
        assert reason is not None and "meridian.example" in reason

        card = score_pair(left, right, veto=reason)
        assert card.veto == reason
        assert card.score == 0.0

    def test_two_people_with_one_name_are_stopped_only_by_the_veto(self) -> None:
        """§10.2's headline case, at its worst: two real people who share a
        name *and* work together. Every positive signal agrees — identical
        names, the same colleagues, the same channel, the same period — and
        co-occurrence makes it worse rather than better, exactly as the section
        warns. The additive score proposes the merge; only the veto stops it.
        """
        shared = {
            "documents": ("documents/a", "documents/b"),
            "channels": ("slack:channel:C0FIN",),
            "neighbours": ("people/mei-tanaka", "people/ana-brito"),
            "seen": (JAN, JAN),
        }
        left = profile(
            "people/sam-kaur", "Sam Kaur", aliases=("sam.kaur@meridian.example",), **shared
        )
        right = profile(
            "people/sam-kaur-2", "Sam Kaur", aliases=("sam.kaur2@meridian.example",), **shared
        )

        unvetoed = score_pair(left, right)
        assert unvetoed.score > Policy().propose_above, (
            "the additive score alone would have proposed merging two real people"
        )

        reason = identity_conflict(left.surfaces, right.surfaces)
        vetoed = score_pair(left, right, veto=reason)
        assert vetoed.veto == reason
        assert vetoed.score == 0.0

    def test_disagreeing_identity_keys_also_drag_the_score_down(self) -> None:
        """Defence in depth. Sam Kaur and Sam Kelly are caught twice: the
        `identity_key` component scores 0.0 rather than being excluded, which
        is enough on its own, and the veto catches it again. Neither is relied
        on alone."""
        left = profile("people/sam-kaur", "Sam Kaur", aliases=("sam.kaur@meridian.example",))
        right = profile(
            "people/sam-kelly", "Sam Kelly", aliases=("sam.kelly@meridian.example",)
        )
        card = score_pair(left, right)
        identity = card.components[0]
        assert identity.applicable and identity.raw == 0.0
        assert card.score < Policy().propose_above
        assert identity_conflict(left.surfaces, right.surfaces) is not None

    def test_a_personal_address_does_not_veto(self) -> None:
        """§10.2's contractor case. Two gmail addresses are not two directory
        accounts, and treating them as a conflict would make the under-merge
        permanent instead of merely likely."""
        left = profile("people/sam-kaur", "Sam Kaur", aliases=("sam.kaur@gmail.com",))
        right = profile("people/s-kaur", "S. Kaur", aliases=("skaur@gmail.com",))
        assert identity_conflict(left.surfaces, right.surfaces) is None

    def test_one_person_with_two_work_addresses_is_not_a_conflict(self) -> None:
        left = profile(
            "people/sam-kaur",
            "Sam Kaur",
            aliases=("sam.kaur@meridian.example", "s.kaur@meridian.example"),
        )
        right = profile("people/s-kaur", "S. Kaur", aliases=("sam.kaur@meridian.example",))
        assert identity_conflict(left.surfaces, right.surfaces) is None


class TestScoring:
    def test_inapplicable_components_leave_the_denominator(self) -> None:
        """A brand-new duplicate has no documents, so three of six components
        have nothing to read. Scoring those as 0.0 would penalise exactly the
        records most likely to *be* duplicates."""
        left = profile("people/sam-kaur", "Sam Kaur", aliases=("sam.kaur@meridian.example",))
        right = profile("people/s-kaur", "S. Kaur", aliases=("sam.kaur@meridian.example",))
        card = score_pair(left, right)

        excluded = [c.name for c in card.components if not c.applicable]
        assert excluded == ["colleague_overlap", "channel_overlap", "temporal_overlap"]
        assert card.score > Policy().propose_above

    def test_a_name_only_person_match_cannot_reach_high_confidence(self) -> None:
        """§10.2: "never auto-merge Person; require >=1 identity-key overlap for
        high confidence". The pair is still proposed — the ceiling is on
        certainty, not on the reviewer seeing it."""
        left = profile("people/sam-kaur", "Sam Kaur")
        right = profile("people/sam-kaur-2", "Sam Kaur")
        card = score_pair(left, right)

        assert not card.has_identity_key
        assert card.capped_from is not None and card.capped_from > card.score
        assert card.score == Policy().cap_without_identity_key
        assert card.score >= Policy().propose_above, "the cap must not mute the proposal"

    def test_an_identical_pair_with_an_identity_key_is_not_capped(self) -> None:
        shared = ("sam.kaur@meridian.example",)
        card = score_pair(
            profile("people/a", "Sam Kaur", aliases=shared),
            profile("people/b", "Sam Kaur", aliases=shared),
        )
        assert card.capped_from is None
        assert card.score > Policy().cap_without_identity_key

    def test_scoring_is_symmetric(self) -> None:
        left = profile(
            "people/a", "Sam Kaur", aliases=("sam.kaur@meridian.example",), documents=("d/1",)
        )
        right = profile("people/b", "S. Kaur", aliases=("sam.kaur@meridian.example",))
        assert score_pair(left, right).score == score_pair(right, left).score

    def test_the_breakdown_names_every_component(self) -> None:
        """A reviewer is being asked to merge two people's records. "0.83" is
        not a reason; the table is the deliverable."""
        card = score_pair(
            profile("people/a", "Sam Kaur", aliases=("sam.kaur@meridian.example",)),
            profile("people/b", "S. Kaur", aliases=("sam.kaur@meridian.example",)),
        )
        table = card.table()
        for component in card.components:
            assert component.name in table
        assert "sam.kaur@meridian.example" in table
        assert f"{card.score:.4f}" in table


class TestProposals:
    def test_the_graph_is_untouched_and_the_proposal_carries_evidence(
        self, repo: Repository
    ) -> None:
        entity(repo, "people/sam-kaur", "Sam Kaur", aliases=("sam.kaur@meridian.example",))
        entity(repo, "people/s-kaur", "S. Kaur", aliases=("sam.kaur@meridian.example",))
        before = {n.id: n for n in repo.walk()}

        report = Layer3Resolver(repo).run()
        assert len(report.proposals) == 1
        proposal = report.proposals[0]
        # Neither record has a document behind it, so the survivor is decided
        # by the stable tie-break rather than by evidence weight.
        assert (proposal.winner, proposal.loser) == ("people/s-kaur", "people/sam-kaur")
        assert proposal.edge.status is EdgeStatus.PROPOSED
        # Quoted as written, not as normalized for matching.
        assert [e.quote for e in proposal.edge.evidence] == ["sam.kaur@meridian.example"]

        SameAsProposalStore(repo).write_all(report.proposals)
        assert {n.id: n for n in repo.walk()} == before, "resolve/ mutated the graph"

    def test_the_better_evidenced_record_survives(self, repo: Repository) -> None:
        """Merging the well-cited record into the sparse one would leave every
        existing citation pointing at a tombstone."""
        entity(repo, "people/sam-kaur", "Sam Kaur", aliases=("sam.kaur@meridian.example",))
        entity(repo, "people/s-kaur", "S. Kaur", aliases=("sam.kaur@meridian.example",))
        _document(repo, "documents/note-aaaaaa", ("people/s-kaur",))

        proposal = Layer3Resolver(repo).run().proposals[0]
        assert proposal.winner == "people/s-kaur"
        assert proposal.loser == "people/sam-kaur"

    def test_pending_speaks_the_review_queues_own_shape(self, repo: Repository) -> None:
        _pair(repo)
        store = SameAsProposalStore(repo)
        store.write_all(Layer3Resolver(repo).run().proposals)

        pending = store.pending()
        assert len(pending) == 1
        assert isinstance(pending[0], PendingEdge)
        assert pending[0].edge.predicate is Predicate.SAME_AS
        assert pending[0].quote(), "a reviewer needs something to check"

    def test_a_rejection_is_recorded_not_deleted(self, repo: Repository) -> None:
        """Mirrors `ReviewQueue.decide`: rejections are the only signal for
        telling a miscalibrated threshold from a working one."""
        _pair(repo)
        store = SameAsProposalStore(repo)
        proposal_id = store.write_all(Layer3Resolver(repo).run().proposals)[0]

        ReviewWorkflow(repo).reject(proposal_id, decided_by="ceo")
        assert store.edge_of(proposal_id).status is EdgeStatus.REJECTED
        assert proposal_id in store.proposal_ids()
        assert store.pending() == []
        assert repo.get("people/s-kaur").frontmatter.status is NodeStatus.ACTIVE

    def test_deciding_twice_is_refused(self, repo: Repository) -> None:
        _pair(repo)
        store = SameAsProposalStore(repo)
        proposal_id = store.write_all(Layer3Resolver(repo).run().proposals)[0]
        store.decide(proposal_id, Decision.ACCEPTED, decided_by="ceo")
        with pytest.raises(SameAsProposalError, match="not pending"):
            store.decide(proposal_id, Decision.REJECTED, decided_by="ceo")

    def test_reopening_restores_the_pre_decision_bytes(self, repo: Repository) -> None:
        """The decision stamp is its own fenced region so that undoing it is a
        deletion rather than a guess at what the prose used to say."""
        _pair(repo)
        store = SameAsProposalStore(repo)
        proposal_id = store.write_all(Layer3Resolver(repo).run().proposals)[0]
        before = store.read(proposal_id)

        store.decide(proposal_id, Decision.REJECTED, decided_by="ceo")
        assert DECISION_REGION in store.read(proposal_id).body

        store.reopen(proposal_id)
        after = store.read(proposal_id)
        assert after.body == before.body
        assert after.frontmatter == before.frontmatter

    def test_process_nodes_are_deferred_and_counted(self, repo: Repository) -> None:
        """§10.3: an LLM names a process differently every time, so string
        matching over those names measures phrasing variance. Not resolving
        them is the decision; *hiding* that would be the bug."""
        entity(repo, "processes/vendor-renewal", "Vendor renewal", node_type=NodeType.PROCESS)
        entity(
            repo,
            "processes/supplier-contract-renewal",
            "Supplier contract renewal",
            node_type=NodeType.PROCESS,
        )
        report = Layer3Resolver(repo).run()
        assert report.proposals == ()
        assert ("Process", 2) in report.deferred
        assert "§10.3" in report.summary()


class TestMergePreconditions:
    """Every case that would make an unmerge inexact, refused before it starts."""

    def test_a_node_cannot_be_merged_into_itself(self, repo: Repository) -> None:
        entity(repo, "people/sam-kaur", "Sam Kaur")
        with pytest.raises(MergeError, match="into itself"):
            Merger(repo).merge("people/sam-kaur", "people/sam-kaur", decided_by="ceo")

    def test_merging_the_same_pair_twice_is_refused(self, repo: Repository) -> None:
        winner, loser = _pair(repo)
        merger = Merger(repo)
        merger.merge(winner, loser, decided_by="ceo")
        with pytest.raises(MergeError, match="already merged"):
            Merger(repo).merge(winner, loser, decided_by="ceo")

    def test_a_node_that_already_redirects_is_refused(self, repo: Repository) -> None:
        winner, loser = _pair(repo)
        entity(repo, "people/third", "Third Person")
        Merger(repo).merge("people/third", loser, decided_by="ceo")
        with pytest.raises(MergeError, match="already redirects"):
            Merger(repo).merge(winner, loser, decided_by="ceo")

    def test_a_missing_node_is_refused(self, repo: Repository) -> None:
        entity(repo, "people/sam-kaur", "Sam Kaur")
        with pytest.raises(MergeError, match="not in the store"):
            Merger(repo).merge("people/sam-kaur", "people/ghost", decided_by="ceo")


class TestUnmergeExactness:
    """Unmerge identifies what it removes by target, never by position."""

    def test_an_unrelated_same_as_edge_survives(self, repo: Repository) -> None:
        entity(repo, "people/other", "Other Person")
        winner, loser = _pair(
            repo,
            winner_relations=(
                Edge(
                    predicate=Predicate.SAME_AS,
                    object="people/other",
                    confidence=1.0,
                    provenance=Provenance.HUMAN,
                    status=EdgeStatus.ACCEPTED,
                ),
            ),
        )
        merger = Merger(repo)
        merger.merge(winner, loser, decided_by="ceo")
        merger.unmerge(winner, loser)

        surviving = [
            e.object
            for e in repo.get(winner).frontmatter.relations
            if e.predicate is Predicate.SAME_AS
        ]
        assert surviving == ["people/other"]

    def test_an_unrelated_redirect_edge_on_the_loser_survives(self, repo: Repository) -> None:
        """A `redirects_to` edge pointing somewhere else predates the merge and
        is not ours to remove. Dropping every `redirects_to` edge — the obvious
        implementation — silently destroys an older rename."""
        entity(repo, "people/ancient", "Ancient Record")
        winner, loser = _pair(
            repo,
            loser_relations=(
                Edge(
                    predicate=Predicate.REDIRECTS_TO,
                    object="people/ancient",
                    confidence=1.0,
                    provenance=Provenance.HUMAN,
                    status=EdgeStatus.ACCEPTED,
                ),
            ),
        )
        merger = Merger(repo)
        merger.merge(winner, loser, decided_by="ceo")
        merger.unmerge(winner, loser)

        restored = repo.get(loser).frontmatter
        assert restored.status is NodeStatus.ACTIVE
        assert restored.redirects_to is None
        assert [
            e.object for e in restored.relations if e.predicate is Predicate.REDIRECTS_TO
        ] == ["people/ancient"]

    def test_the_round_trip_is_byte_identical(self, repo: Repository) -> None:
        from company_brain.store.serialize import dump_node

        winner, loser = _pair(repo, loser_body="Hand-written note about this record.")
        before = {node.id: dump_node(node) for node in repo.walk()}

        merger = Merger(repo)
        merger.merge(winner, loser, decided_by="ceo", evidence=(Evidence(quote="x"),))
        assert {node.id: dump_node(node) for node in repo.walk()} != before

        merger.unmerge(winner, loser)
        assert {node.id: dump_node(node) for node in repo.walk()} == before

    def test_unmerging_an_active_node_is_refused(self, repo: Repository) -> None:
        winner, loser = _pair(repo)
        with pytest.raises(MergeError, match="not merged"):
            Merger(repo).unmerge(winner, loser)

    def test_a_half_applied_merge_can_still_be_reversed(self, repo: Repository) -> None:
        """The two writes are individually atomic but not atomic together
        (invariant 14 is per file). The repair path must be no fussier than the
        damage, or a crash mid-merge becomes permanent."""
        winner, loser = _pair(repo)
        merger = Merger(repo)
        merger.merge(winner, loser, decided_by="ceo")

        # Simulate losing the winner's edge — the half that carries no tombstone.
        from company_brain.resolve.merge import _drop_same_as

        repo.put(_drop_same_as(repo.get(winner), loser))
        merger.unmerge(winner, loser)
        assert repo.get(loser).frontmatter.status is NodeStatus.ACTIVE

    def test_a_merged_node_is_not_a_candidate_for_a_second_merge(
        self, repo: Repository
    ) -> None:
        winner, loser = _pair(repo)
        Merger(repo).merge(winner, loser, decided_by="ceo")
        assert Layer3Resolver(repo).run().proposals == ()


class TestDeterminism:
    """Invariant 3 territory. Layer 3 sits on sets and dicts throughout."""

    def test_two_runs_agree(self, repo: Repository) -> None:
        _pair(repo)
        entity(repo, "people/priya-raman", "Priya Raman", aliases=("priya@meridian.example",))
        entity(repo, "people/arjun-raman", "Arjun Raman", aliases=("arjun@meridian.example",))

        first, second = Layer3Resolver(repo).run(), Layer3Resolver(repo).run()
        assert [p.proposal_id for p in first.proposals] == [
            p.proposal_id for p in second.proposals
        ]
        assert [c.score for c in first.considered] == [c.score for c in second.considered]

    def test_proposals_come_back_sorted(self, repo: Repository) -> None:
        for i in range(6):
            entity(
                repo,
                f"people/dup{i}",
                "Sam Kaur",
                aliases=(f"sam.kaur+{i}@meridian.example",),
            )
        proposals = Layer3Resolver(repo).run().proposals
        assert len(proposals) > 1
        keys = [(-p.score, p.winner, p.loser) for p in proposals]
        assert keys == sorted(keys)

    def test_output_is_stable_across_hash_seeds(self, tmp_path: Path) -> None:
        """The one check that cannot be made from inside a single process.

        `PYTHONHASHSEED` randomises `str.__hash__`, so an accidental dependence
        on set or dict iteration order shows up here and nowhere else.
        """
        script = textwrap.dedent(
            """
            import hashlib, sys
            from pathlib import Path
            from company_brain.resolve import Layer3Resolver, SameAsProposalStore
            from company_brain.schemas.acl import AclRef, Sensitivity
            from company_brain.schemas.nodes import Frontmatter, Node, NodeType
            from company_brain.store.backend import LocalFsBackend
            from company_brain.store.repository import Repository

            repo = Repository(LocalFsBackend(Path(sys.argv[1])))
            for slug, title, aliases in [
                ("sam-kaur", "Sam Kaur", ("sam.kaur@meridian.example",)),
                ("s-kaur", "S. Kaur", ("sam.kaur@meridian.example",)),
                ("samantha-kaur", "Samantha Kaur", ("s.kaur@meridian.example",)),
                ("priya-raman", "Priya Raman", ("priya@meridian.example",)),
                ("arjun-raman", "Arjun Raman", ("arjun@meridian.example",)),
                ("mei-tanaka", "Mei Tanaka", ("mei@meridian.example",)),
            ]:
                repo.put(Node(frontmatter=Frontmatter(
                    id=f"people/{slug}", type=NodeType.PERSON, title=title,
                    acl=AclRef(ref="fs:corpus:docs", sensitivity=Sensitivity.INTERNAL),
                    aliases=aliases)))

            report = Layer3Resolver(repo).run()
            SameAsProposalStore(repo).write_all(report.proposals)
            digest = hashlib.sha256()
            digest.update(report.summary().encode())
            for proposal in report.proposals:
                digest.update(proposal.proposal_id.encode())
                digest.update(f"{proposal.score:.6f}".encode())
                digest.update(proposal.card.table().encode())
                digest.update(repr(proposal.edge.evidence).encode())
            for path in sorted(Path(sys.argv[1]).rglob("*.md")):
                digest.update(path.read_bytes())
            print(digest.hexdigest())
            """
        )
        runner = tmp_path / "run.py"
        runner.write_text(script)

        digests = []
        for seed in ("0", "1"):
            store = tmp_path / f"store-{seed}"
            env = os.environ | {"PYTHONHASHSEED": seed, "COMPANY_BRAIN_OFFLINE": "1"}
            done = subprocess.run(
                [sys.executable, str(runner), str(store)],
                capture_output=True,
                text=True,
                env=env,
                check=True,
                cwd=Path(__file__).resolve().parents[2],
            )
            digests.append(done.stdout.strip())

        assert digests[0] == digests[1], "layer 3 output depends on the hash seed"


# ---- fixtures -----------------------------------------------------------


def _pair(
    repo: Repository,
    *,
    winner_relations: tuple[Edge, ...] = (),
    loser_relations: tuple[Edge, ...] = (),
    loser_body: str = "",
) -> tuple[str, str]:
    """A duplicate pair that layer 3 proposes and a merge can act on."""
    entity(
        repo,
        "people/sam-kaur",
        "Sam Kaur",
        aliases=("sam.kaur@meridian.example",),
        relations=winner_relations,
    )
    entity(
        repo,
        "people/s-kaur",
        "S. Kaur",
        aliases=("sam.kaur@meridian.example",),
        relations=loser_relations,
        body=loser_body,
    )
    return "people/sam-kaur", "people/s-kaur"


def _document(repo: Repository, node_id: str, mentions: tuple[str, ...]) -> None:
    from company_brain.schemas.nodes import SourceRef

    repo.put(
        Node(
            frontmatter=Frontmatter(
                id=node_id,
                type=NodeType.DOCUMENT,
                title="A note",
                acl=AclRef(ref="fs:corpus:docs", sensitivity=INTERNAL),
                source=SourceRef(
                    connector="test",
                    uri="file://note",
                    external_id="note",
                    content_sha256="0" * 64,
                ),
                relations=tuple(
                    Edge(
                        predicate=Predicate.MENTIONS,
                        object=target,
                        confidence=1.0,
                        provenance=Provenance.STRUCTURAL,
                        status=EdgeStatus.ACCEPTED,
                    )
                    for target in mentions
                ),
            ),
            body="Sam Kaur was mentioned here.",
        )
    )
