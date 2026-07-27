"""The M3 entity-resolution gate.

One criterion from ROADMAP M3 binds this whole module:

    A merge, then an unmerge, then a re-ingest returns the store to a
    byte-identical state.

It is written first, deliberately, because it kills the obvious merge
implementation. The obvious implementation calls ``Repository.redirect`` on the
losing node, which replaces its body with ``Merged into [[winner]]``. That is
lossy: unmerge can restore ``status`` and ``redirects_to`` from the schema, but
it cannot invent the prose it overwrote, and ``LocalIngest._write_entities``
skips nodes that already exist (invariant 13) so a re-ingest will never repair
it either. The tree comes back different and this test fails.

So the merge here is written as an *exactly invertible pair of edits*: the
losing node keeps every byte of its body and frontmatter, gaining only the
tombstone fields, and the winner gains exactly one ``same_as`` edge. §10.1 says
a merge "never destroys the losing node" — keeping its prose is what that
sentence has to mean if unmerge is a real operation rather than a cleanup
script.

The path under test is the whole one a reviewer walks: propose -> accept ->
regret it -> revert. Accepting stamps the proposal file too, and the proposal
file lives inside the store, so a revert that forgot to unstamp it would also
show up here as a changed tree.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from company_brain.app import build_app, cached_extractor
from company_brain.connectors.local_fs import LocalIngest
from company_brain.corpus.generate import generate
from company_brain.resolve import (
    Layer3Resolver,
    MergeError,
    ReviewWorkflow,
    SameAsProposalStore,
)
from company_brain.schemas.acl import AclRef, Sensitivity
from company_brain.schemas.nodes import Frontmatter, Node, NodeStatus, NodeType
from company_brain.store.repository import Repository

pytestmark = pytest.mark.acceptance

# A second directory record for a person who already exists. Shares Sam Kaur's
# corporate email, so layer 3 has an identity key to work with rather than a
# name alone — the case §10.1 says should score high and still only propose.
DUPLICATE_ID = "people/s-kaur"
DUPLICATE_BODY = (
    "Record created from a forwarded thread; no directory entry at the time.\n\n"
    "This prose is the point of the test: a merge must not eat it."
)


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def plant_duplicate(repo: Repository) -> None:
    repo.put(
        Node(
            frontmatter=Frontmatter(
                id=DUPLICATE_ID,
                type=NodeType.PERSON,
                title="S. Kaur",
                acl=AclRef(ref="fs:corpus:docs", sensitivity=Sensitivity.INTERNAL),
                aliases=("S. Kaur", "sam.kaur@meridian.example"),
            ),
            body=DUPLICATE_BODY,
        )
    )


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    """Corpus plus an ingested store, with one planted duplicate person.

    Only ``corpus/docs`` is ingested. ``_write_entities`` writes the full
    curated roster regardless of which documents were read, so every entity
    node this module needs exists, and the module costs a fraction of a full
    201-document ingest.
    """
    base = tmp_path_factory.mktemp("m3")
    corpus, store = base / "corpus", base / "store"
    generate(corpus)

    app = build_app(store)
    report = LocalIngest(
        app.repo, app.registry, cached_extractor(app, store, frozen=False)
    ).run(corpus / "docs")
    assert not report.skipped, report.skipped[:3]
    plant_duplicate(app.repo)
    return corpus / "docs", store


def reingest(corpus: Path, store: Path) -> None:
    """Frozen re-ingest: a cache miss would mean this test measured the
    extractor's mood rather than the merge's reversibility."""
    app = build_app(store)
    report = LocalIngest(app.repo, app.registry, cached_extractor(app, store, frozen=True)).run(
        corpus
    )
    assert report.cache_misses == 0, "frozen re-ingest called the extractor"


@pytest.fixture()
def proposed(built: tuple[Path, Path]) -> tuple[Path, Path, str]:
    """Run layer 3 and persist its proposals. Returns the duplicate's proposal id.

    Module-scoped ``built`` is shared, so every test that mutates the store must
    put it back; each does, and the byte-identity test is what proves it.
    """
    corpus, store = built
    repo = build_app(store).repo
    proposals = Layer3Resolver(repo).run().proposals
    SameAsProposalStore(repo).write_all(proposals)
    match = next(p for p in proposals if DUPLICATE_ID in (p.winner, p.loser))
    return corpus, store, match.proposal_id


class TestReversibleMerge:
    """The binding criterion."""

    def test_merge_then_unmerge_then_reingest_is_byte_identical(
        self, proposed: tuple[Path, Path, str]
    ) -> None:
        corpus, store, proposal_id = proposed
        before = tree_hash(store)

        workflow = ReviewWorkflow(build_app(store).repo)
        record = workflow.accept(proposal_id, decided_by="ceo")
        assert tree_hash(store) != before, "accepting a merge changed nothing"

        workflow = ReviewWorkflow(build_app(store).repo)
        workflow.revert(proposal_id)
        reingest(corpus, store)

        assert tree_hash(store) == before, (
            f"merge of {record.loser} into {record.winner} did not fully reverse"
        )

    def test_the_losing_node_keeps_its_prose_through_the_round_trip(
        self, proposed: tuple[Path, Path, str]
    ) -> None:
        """The specific thing a redirect-based merge destroys.

        Asserted at both ends: during the merge (the node is tombstoned but not
        gutted) and after the revert (it is fully back).
        """
        corpus, store, proposal_id = proposed
        workflow = ReviewWorkflow(build_app(store).repo)
        workflow.accept(proposal_id, decided_by="ceo")

        merged = build_app(store).repo.get(DUPLICATE_ID)
        assert merged.frontmatter.status is NodeStatus.MERGED
        assert merged.body == DUPLICATE_BODY, "the merge ate the losing node's body"

        ReviewWorkflow(build_app(store).repo).revert(proposal_id)
        reingest(corpus, store)

        restored = build_app(store).repo.get(DUPLICATE_ID)
        assert restored.frontmatter.status is NodeStatus.ACTIVE
        assert restored.frontmatter.redirects_to is None
        assert restored.body == DUPLICATE_BODY

    def test_old_citations_still_resolve_while_merged(
        self, proposed: tuple[Path, Path, str]
    ) -> None:
        """Invariant 12. A citation issued before the merge must land on the
        surviving node, not dangle."""
        corpus, store, proposal_id = proposed
        workflow = ReviewWorkflow(build_app(store).repo)
        record = workflow.accept(proposal_id, decided_by="ceo")

        repo = build_app(store).repo
        assert repo.resolve(record.loser).id == record.winner

        ReviewWorkflow(build_app(store).repo).revert(proposal_id)
        reingest(corpus, store)
        assert build_app(store).repo.resolve(record.loser).id == record.loser


class TestProposalsOnly:
    """Nothing in resolve/ mutates the graph (invariant 9's rule, applied to a
    non-agent writer — the reasoning is identical)."""

    def test_running_the_resolver_touches_only_the_proposal_tree(
        self, built: tuple[Path, Path]
    ) -> None:
        _, store = built
        repo = build_app(store).repo
        graph_before = {node.id: node for node in repo.walk()}

        proposals = Layer3Resolver(repo).run().proposals
        assert proposals, "the planted duplicate produced no proposal at all"
        SameAsProposalStore(repo).write_all(proposals)

        fresh = build_app(store).repo
        assert {node.id: node for node in fresh.walk()} == graph_before
        written = list(fresh.walk_proposal_ids())
        assert any(p.proposal_id in written for p in proposals)

    def test_a_proposal_is_never_auto_accepted(self, built: tuple[Path, Path]) -> None:
        """GATES[same_as] has no auto-accept threshold at any confidence, and
        §10.2 says Person never auto-merges. Both are asserted on the artefact
        rather than trusted from the table."""
        _, store = built
        repo = build_app(store).repo
        for proposal in Layer3Resolver(repo).run().proposals:
            assert proposal.edge.status.value == "proposed"
            assert proposal.edge.evidence, f"{proposal.proposal_id} cites nothing"


class TestMergePreconditions:
    """The cases that would quietly make a merge irreversible, refused up front."""

    def test_unmerging_something_that_was_never_merged_is_refused(
        self, built: tuple[Path, Path]
    ) -> None:
        from company_brain.resolve import Merger

        _, store = built
        merger = Merger(build_app(store).repo)
        with pytest.raises(MergeError, match="not merged"):
            merger.unmerge("people/sam-kaur", DUPLICATE_ID)

    def test_merging_across_types_is_refused(self, built: tuple[Path, Path]) -> None:
        from company_brain.resolve import Merger

        _, store = built
        merger = Merger(build_app(store).repo)
        team = next(build_app(store).repo.walk_ids("Team"))
        with pytest.raises(MergeError, match="type"):
            merger.merge("people/sam-kaur", team, decided_by="ceo")
