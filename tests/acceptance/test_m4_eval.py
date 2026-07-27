"""The M4 evaluation gate.

ROADMAP M4 asks for 100+ golden questions across five classes, recall@k tracked
per principal class, and no regression against the M1 goldens. This is that,
executable.

The gate lands *before* the M4 features it grades, so most of these tests pin
measurement rather than quality: that the goldens still describe the corpus,
that recall is measured against what each principal can actually see, that a
leak is caught on every question rather than on a hand-planted canary, and that
today's numbers are recorded so tomorrow's cannot quietly fall below them.

The systemic and unanswerable classes score badly right now. That is the point:
they are the milestone's target, and the baseline is the starting line.
"""

from __future__ import annotations

from collections import Counter

import pytest

from company_brain.app import App
from company_brain.corpus.generate import channel_id
from company_brain.eval.baseline import compare, load_baseline
from company_brain.eval.harness import EvalReport, run_eval
from company_brain.eval.questions import (
    DOCS,
    EMAIL,
    GOLDENS,
    SLACK_CHANNELS,
    VISIBLE_SOURCES,
    QuestionClass,
    source_of,
    visible_evidence,
)
from company_brain.schemas.acl import Sensitivity

pytestmark = pytest.mark.acceptance

PRINCIPALS = ("ceo", "support-lead", "eng-ic", "contractor")

# The ACL ref each source family maps onto. Restated here, like VISIBLE_SOURCES
# itself, so the derivation used for leak checking is checked against the store
# rather than assumed.
FAMILY_REFS = {
    DOCS: "fs:corpus:docs",
    EMAIL: "gmail:mailbox:meridian",
    **{f"slack:{name}": f"slack:channel:{channel_id(name)}" for name in SLACK_CHANNELS},
}


@pytest.fixture(scope="module")
def report(indexed_app: App) -> EvalReport:
    return run_eval(indexed_app, principals=PRINCIPALS)


class TestTheGoldenSet:
    def test_it_is_large_enough_and_covers_every_class(self) -> None:
        counts = Counter(g.qclass for g in GOLDENS)
        assert len(GOLDENS) >= 100, f"only {len(GOLDENS)} goldens"
        for qclass in QuestionClass:
            assert counts[qclass] >= 10, f"{qclass} has only {counts[qclass]} questions"

    def test_question_text_is_unique(self) -> None:
        questions = [g.question for g in GOLDENS]
        duplicates = [q for q, n in Counter(questions).items() if n > 1]
        assert not duplicates, duplicates

    def test_every_expected_pattern_resolves_to_a_real_node(self, indexed_app: App) -> None:
        """The anti-rot guard.

        Goldens are built from the corpus generator's tables, so a renamed
        process moves the question and its expected evidence together — but the
        *path* shapes are hand-written, and a change to how document IDs are
        derived would silently turn every expectation into a permanent miss that
        looks like a quality problem. Cheaper to assert it.
        """
        ids = list(indexed_app.repo.walk_ids())
        orphans = sorted(
            {
                pattern
                for golden in GOLDENS
                for pattern in golden.evidence
                if not any(pattern in node_id for node_id in ids)
            }
        )
        assert not orphans, f"expected evidence matches no node in the store: {orphans}"

    def test_the_m1_goldens_are_carried_over_verbatim(self) -> None:
        """`test_m1.py::SEEDED` is the M1 acceptance criterion; M4 must not
        quietly re-word it into something easier."""
        from tests.acceptance.test_m1 import SEEDED

        seeded = {g.question: g.evidence for g in GOLDENS if g.seeded}
        assert len(seeded) == len(SEEDED)
        for question, expected in SEEDED:
            assert question in seeded, f"M1 golden dropped: {question!r}"
            assert seeded[question] == (expected,), question

    def test_unanswerable_questions_expect_no_evidence(self) -> None:
        for golden in GOLDENS:
            if golden.qclass is QuestionClass.UNANSWERABLE:
                assert not golden.evidence, golden.id


class TestVisibilityIsRestatedNotDerived:
    """The harness carries its own model of who sees what.

    If it asked `AccessFilter` instead, a widened grant would widen the
    expectation with it and the eval would report a leak as a pass. These two
    tests are what make the independent restatement worth having.
    """

    def test_every_family_maps_onto_a_ref_the_store_actually_uses(
        self, indexed_app: App
    ) -> None:
        seen: dict[str, set[str]] = {}
        for node in indexed_app.repo.walk():
            family = source_of(node.frontmatter.id)
            seen.setdefault(family, set()).add(node.frontmatter.acl.ref)

        for family, refs in sorted(seen.items()):
            assert refs == {FAMILY_REFS[family]}, (
                f"family {family!r} spans refs {sorted(refs)}, expected "
                f"{FAMILY_REFS[family]!r} — the leak check derives the family "
                f"from the node ID and would now derive it wrongly"
            )

    @pytest.mark.parametrize("principal", PRINCIPALS)
    def test_it_agrees_with_the_grant_table(self, indexed_app: App, principal: str) -> None:
        access = indexed_app.access(indexed_app.principal(principal))
        tiers = {
            node.frontmatter.acl.ref: node.frontmatter.acl.sensitivity
            for node in indexed_app.repo.walk()
        }
        for family, ref in sorted(FAMILY_REFS.items()):
            expected = family in VISIBLE_SOURCES[principal]
            actual = access.allows(ref, tiers.get(ref, Sensitivity.RESTRICTED))
            assert actual == expected, (
                f"{principal} {'can' if actual else 'cannot'} read {family} "
                f"({ref}), but the harness expects the opposite"
            )


class TestPerPrincipalRecall:
    """Criterion: recall@k per principal class, so a permission cliff fails a
    test rather than reading as a quality problem."""

    def test_recall_is_scored_against_visible_evidence_only(self) -> None:
        answerable = [g for g in GOLDENS if g.answerable and g.evidence]
        ceo = [g for g in answerable if visible_evidence(g, "ceo")]
        contractor = [g for g in answerable if visible_evidence(g, "contractor")]
        assert len(ceo) == len(answerable), "the CEO should be able to reach every question"
        assert not contractor, (
            "the contractor holds only the general channel, so no question's "
            "evidence is visible to them — scoring recall over the full set "
            "would report that boundary as a retrieval failure"
        )

    def test_a_principal_who_can_see_the_evidence_finds_it(self, report: EvalReport) -> None:
        """The cliff detector. The CEO, support lead and engineer all hold the
        docs and mailbox grants, so on questions whose evidence lives there
        their recall must agree. A gap means retrieval leaked a permission
        decision into ranking."""
        by_principal = report.by_principal
        docs_readers = ("ceo", "support-lead", "eng-ic")
        recalls = {p: by_principal[p].recall_at_k for p in docs_readers}
        spread = max(recalls.values()) - min(recalls.values())
        assert spread < 0.05, f"recall differs across equally-granted principals: {recalls}"

    def test_the_contractor_is_measured_on_refusals_not_recall(
        self, report: EvalReport
    ) -> None:
        contractor = report.by_principal["contractor"]
        assert contractor.graded == 0
        assert contractor.refusal_expected == len(GOLDENS)


class TestLeaks:
    """Every question is a leak test, for every principal — 440 of them."""

    def test_no_question_surfaces_a_node_the_principal_cannot_see(
        self, report: EvalReport
    ) -> None:
        leaks = report.leaks
        assert not leaks, [
            f"[{r.principal}] {r.question_id}: {list(r.leaked)[:3]}" for r in leaks[:5]
        ]

    def test_the_canary_channel_is_never_reached_by_anyone_but_the_ceo(
        self, report: EvalReport
    ) -> None:
        for result in report.results:
            if result.principal == "ceo":
                continue
            surfaced = [n for n in (*result.retrieved, *result.cited) if "leadership-comp" in n]
            assert not surfaced, f"[{result.principal}] {result.question_id}: {surfaced}"


class TestRegressionGate:
    def test_no_regression_against_the_committed_baseline(self, report: EvalReport) -> None:
        regressions = compare(report, load_baseline())
        assert not regressions, "\n".join(str(r) for r in regressions)

    def test_the_m1_goldens_do_not_regress_at_all(self, report: EvalReport) -> None:
        """ROADMAP M4: "no regression versus M3 on the M1 goldens". Zero
        tolerance, separately from the aggregate gate that allows a little."""
        assert report.seeded.recall_at_k == 1.0
        assert report.seeded.hit_rate == 1.0
        assert report.seeded.errors == 0

    def test_the_report_is_deterministic(self, indexed_app: App) -> None:
        """A baseline you cannot reproduce is not a gate. Retrieval is
        deterministic by construction (invariant 3); this asserts the harness
        did not smuggle in set iteration order on top of it."""
        first = run_eval(indexed_app, principals=("ceo", "contractor")).to_json()
        second = run_eval(indexed_app, principals=("ceo", "contractor")).to_json()
        assert first == second

    def test_the_baseline_file_is_committed_and_current(self) -> None:
        baseline = load_baseline()
        assert baseline["k"] == 10
        assert baseline["synthesizer"] == "extractive-offline", (
            "the committed baseline must come from an offline run; an online "
            "baseline cannot be reproduced in CI"
        )
        assert baseline["principals"] == list(PRINCIPALS)
        assert baseline["overall"]["questions"] == len(GOLDENS) * len(PRINCIPALS)


class TestWhatTheHarnessSaysIsStillMissing:
    """The measurements M4 exists to move. Pinned as assertions on the *shape*
    of the gap, not on the number, so improving them fails nothing."""

    def test_the_insufficient_evidence_path_is_measured(self, report: EvalReport) -> None:
        unanswerable = report.by_class[QuestionClass.UNANSWERABLE.value]
        assert unanswerable.refusal_expected == 14 * len(PRINCIPALS)
        # The metric exists and is recorded; the rate itself is the M4 target
        # and is gated by the baseline rather than asserted here.
        assert 0.0 <= unanswerable.refusal_rate <= 1.0

    def test_systemic_questions_are_the_weakest_class(self, report: EvalReport) -> None:
        """Documented, not lamented: systemic queries are answered today only
        insofar as a process page happens to describe its own handoffs. When
        process modelling and handoff enrichment land this stops being true,
        and the assertion below is the thing that should be deleted."""
        by_class = report.by_class
        assert by_class[QuestionClass.SYSTEMIC.value].graded > 0
        assert (
            by_class[QuestionClass.SYSTEMIC.value].recall_at_k
            < by_class[QuestionClass.TEMPORAL.value].recall_at_k
        )
