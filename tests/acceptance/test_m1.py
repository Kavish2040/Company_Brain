"""The M1 acceptance gate.

Five criteria from ROADMAP M1:

1. `cb ask` answers 10 seeded questions with correct citations
2. full re-ingestion produces a byte-identical markdown tree
3. rebuild-from-scratch matches the incremental index
4. the permission test — different answers per principal, and the planted
   private comp discussion is never retrievable by a non-CEO principal
5. `cb doctor` is clean

Criterion 4 is the one that matters most. Everything else is a correctness bug;
a leak is the thing that ends the company.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest

from company_brain.app import build_app, cached_extractor
from company_brain.connectors.local_fs import LocalIngest
from company_brain.corpus.generate import generate
from company_brain.retrieve.hybrid import HybridRetriever
from company_brain.synthesize.answer import (
    CitationLeakError,
    ExtractiveSynthesizer,
    UncitedAnswerError,
    validate,
)

pytestmark = pytest.mark.acceptance

# (question, a node ID substring that must appear in the citations)
SEEDED: list[tuple[str, str]] = [
    ("who owns vendor renewals?", "vendor-renewal"),
    ("who is responsible for incident response?", "incident-response"),
    ("what is the customer escalation process?", "customer-escalation"),
    ("who owns quarterly close?", "quarterly-close"),
    ("what does the release sign-off process involve?", "release-sign-off"),
    ("which team owns security review?", "security-review"),
    ("what is Project Snowflake?", "snowflake"),
    ("who handles refund approval?", "refund-approval"),
    ("what happens during employee onboarding?", "onboarding"),
    ("who owns capacity planning?", "capacity-planning"),
]


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    """Generate a corpus and ingest it once for the whole module."""
    base = tmp_path_factory.mktemp("m1")
    corpus, store = base / "corpus", base / "store"
    generate(corpus)

    app = build_app(store)
    ingest = LocalIngest(app.repo, app.registry, cached_extractor(app, store, frozen=False))
    report = ingest.run(corpus)
    assert report.documents == 201
    assert not report.skipped
    return corpus, store


class TestDeterminism:
    def test_corpus_regenerates_byte_identically(self, tmp_path: Path) -> None:
        a, b = tmp_path / "a", tmp_path / "b"
        generate(a)
        generate(b)
        assert tree_hash(a) == tree_hash(b)

    def test_reingest_produces_byte_identical_tree(
        self, built: tuple[Path, Path], tmp_path: Path
    ) -> None:
        """Criterion 2. Frozen mode: a cache miss is an error, so this tests our
        pipeline rather than the provider's mood."""
        corpus, store = built
        before = tree_hash(store)

        app = build_app(store)
        ingest = LocalIngest(app.repo, app.registry, cached_extractor(app, store, frozen=True))
        report = ingest.run(corpus)

        assert report.cache_misses == 0, "frozen re-ingest called the extractor"
        assert tree_hash(store) == before

    def test_frozen_mode_refuses_an_uncached_document(
        self, built: tuple[Path, Path], tmp_path: Path
    ) -> None:
        from company_brain.extract.base import CacheMiss

        corpus, store = built
        fresh = tmp_path / "fresh"
        shutil.copytree(corpus, fresh)
        (fresh / "docs" / "brand-new.md").write_text("# Brand new\n\nUnseen content.\n")

        app = build_app(store)
        ingest = LocalIngest(app.repo, app.registry, cached_extractor(app, store, frozen=True))
        report = ingest.run(fresh)
        assert any(
            isinstance_name(e) == "CacheMiss" or "no cached extraction" in e
            for _, e in report.skipped
        ), report.skipped[:3]
        assert CacheMiss is not None


def isinstance_name(message: str) -> str:
    return message


class TestIndexRebuild:
    def test_rebuild_is_reproducible(self, built: tuple[Path, Path]) -> None:
        """Criterion 3 — invariant 2 in executable form."""
        _, store = built
        first = build_app(store)
        first.load_index()
        second = build_app(store)
        second.load_index()
        assert first.index.stats() == second.index.stats()
        assert first.index.stats()["nodes"] == 232


class TestSeededQuestions:
    @pytest.mark.parametrize(("question", "expected"), SEEDED, ids=[q for q, _ in SEEDED])
    def test_answers_with_correct_citation(
        self, built: tuple[Path, Path], question: str, expected: str
    ) -> None:
        """Criterion 1."""
        _, store = built
        app = build_app(store)
        app.load_index()
        access = app.access(app.principal("ceo"))

        retrieval = HybridRetriever(app.index, access).retrieve(question, limit=6)
        answer = ExtractiveSynthesizer().synthesize(question, retrieval, app.index)
        validate(answer, retrieval, access, app.index)

        assert answer.citations, f"no citations for {question!r}"
        cited = " ".join(c.node_id for c in answer.citations)
        assert expected in cited, f"{question!r} cited {cited!r}, expected {expected!r}"


class TestPermissions:
    """Criterion 4. The leak canary."""

    def test_principals_see_different_amounts(self, built: tuple[Path, Path]) -> None:
        _, store = built
        app = build_app(store)
        sizes = {
            name: len(app.access(app.principal(name)).refs)
            for name in ("ceo", "support-lead", "eng-ic", "contractor")
        }
        assert sizes["ceo"] > sizes["support-lead"] > sizes["eng-ic"] > sizes["contractor"]

    @pytest.mark.parametrize("principal", ["support-lead", "eng-ic", "contractor"])
    def test_private_comp_channel_never_retrievable(
        self, built: tuple[Path, Path], principal: str
    ) -> None:
        """The planted restricted channel must not surface for anyone but the CEO.

        Asserted at the retrieval layer AND the citation layer independently —
        two checks, because a single bug in one of them is a headline.
        """
        _, store = built
        app = build_app(store)
        app.load_index()
        access = app.access(app.principal(principal))

        for question in ("compensation bands", "leadership comp discussion", "comp"):
            retrieval = HybridRetriever(app.index, access).retrieve(question, limit=10)
            for node in retrieval.nodes:
                assert "leadership-comp" not in node.node_id, (
                    f"{principal} retrieved {node.node_id} for {question!r}"
                )
            answer = ExtractiveSynthesizer().synthesize(question, retrieval, app.index)
            assert "leadership-comp" not in answer.text
            validate(answer, retrieval, access, app.index)

    def test_ceo_can_reach_the_restricted_channel(self, built: tuple[Path, Path]) -> None:
        # The canary must be reachable by *someone*, or the test above passes
        # trivially and proves nothing.
        _, store = built
        app = build_app(store)
        app.load_index()
        access = app.access(app.principal("ceo"))
        retrieval = HybridRetriever(app.index, access).retrieve(
            "compensation bands Engineering ladder", limit=10
        )
        assert any("leadership-comp" in n.node_id for n in retrieval.nodes)

    def test_answers_differ_by_principal(self, built: tuple[Path, Path]) -> None:
        _, store = built
        app = build_app(store)
        app.load_index()
        texts = {}
        for principal in ("ceo", "contractor"):
            access = app.access(app.principal(principal))
            retrieval = HybridRetriever(app.index, access).retrieve(
                "who owns vendor renewals?", limit=6
            )
            texts[principal] = (
                ExtractiveSynthesizer()
                .synthesize("who owns vendor renewals?", retrieval, app.index)
                .text
            )
        assert texts["ceo"] != texts["contractor"]


class TestCitationContract:
    """Invariant 11 — an uncited answer is an error, not a degraded response."""

    def test_fabricated_citation_is_rejected(self, built: tuple[Path, Path]) -> None:
        _, store = built
        app = build_app(store)
        app.load_index()
        access = app.access(app.principal("ceo"))
        retrieval = HybridRetriever(app.index, access).retrieve("vendor renewal", limit=4)

        from company_brain.synthesize.answer import Answer

        forged = Answer(
            question="q",
            text="Sam Kaur owns vendor renewals. [[documents/does/not/exist-000000]]",
        )
        with pytest.raises(UncitedAnswerError, match="fabricated citation"):
            validate(forged, retrieval, access, app.index)

    def test_uncited_answer_is_rejected(self, built: tuple[Path, Path]) -> None:
        _, store = built
        app = build_app(store)
        app.load_index()
        access = app.access(app.principal("ceo"))
        retrieval = HybridRetriever(app.index, access).retrieve("vendor renewal", limit=4)

        from company_brain.synthesize.answer import Answer

        with pytest.raises(UncitedAnswerError):
            validate(
                Answer(question="q", text="Sam Kaur owns vendor renewals, obviously."),
                retrieval,
                access,
                app.index,
            )

    def test_citing_an_invisible_node_raises_a_leak(self, built: tuple[Path, Path]) -> None:
        _, store = built
        app = build_app(store)
        app.load_index()

        ceo = app.access(app.principal("ceo"))
        comp = next(
            n.node_id
            for n in HybridRetriever(app.index, ceo)
            .retrieve("compensation bands", limit=10)
            .nodes
            if "leadership-comp" in n.node_id
        )
        retrieval = HybridRetriever(app.index, ceo).retrieve("compensation bands", limit=10)

        from company_brain.synthesize.answer import Answer

        contractor = app.access(app.principal("contractor"))
        with pytest.raises(CitationLeakError):
            validate(
                Answer(
                    question="q",
                    text=f"Compensation bands are being revisited before Q3. [[{comp}]]",
                ),
                retrieval,
                contractor,
                app.index,
            )


class TestAgentBoundary:
    """Invariant 8 and 9."""

    def test_agent_visibility_is_intersected_with_the_human(
        self, built: tuple[Path, Path]
    ) -> None:
        from company_brain.mcp.server import Session

        _, store = built
        app = build_app(store)
        app.load_index()

        # An agent that itself holds CEO-level grants, delegated by a contractor,
        # must see only what the contractor sees.
        app.grants.grant(
            "agent-x",
            "slack:channel:C0LEAD",
            __import__(
                "company_brain.schemas.acl", fromlist=["Sensitivity"]
            ).Sensitivity.RESTRICTED,
        )
        session = Session(app=app, agent_id="agent-x", delegated_by="contractor")
        assert "slack:channel:C0LEAD" not in session.access.refs

    def test_write_node_produces_a_proposal_not_a_mutation(
        self, built: tuple[Path, Path]
    ) -> None:
        from company_brain.mcp.server import McpTools, Session

        _, store = built
        app = build_app(store)
        app.load_index()
        session = Session(app=app, agent_id="agent-x", delegated_by="ceo")
        target = next(app.repo.walk_ids("Person"))
        before = app.repo.get(target)

        result = McpTools(session).write_node(target, {"body": "AGENT WROTE THIS"})

        assert result["state"] == "pending_review"
        assert app.repo.get(target).body == before.body, "agent mutated the graph"
        assert result["proposal_id"] in list(app.repo.walk_proposal_ids())
