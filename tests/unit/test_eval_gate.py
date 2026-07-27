"""The regression gate's own tests.

`tests/acceptance/test_m4_eval.py` only exercises the *passing* path — a gate
that has never been seen to fail is not known to be a gate. These run the real
golden set through the gate and break it one way at a time, without paying for
an ingest.

Every report here is built from :data:`GOLDENS` and
:func:`questions.visible_evidence`, so a "regression" means *this question
stopped returning the right answer for this principal* — the thing the gate
claims to measure. Reports of interchangeable dummy results cannot say that: the
denominators are wrong, the per-class and per-principal blocks are empty, and a
drop of "one in a hundred" corresponds to nothing that could happen to the
pipeline. The shapes of damage modelled below are the ones that actually occur:

* a question **misses entirely** — nothing it should have cited was retrieved;
* a question goes **partial** — it still finds the process page but no longer
  the runbook, which is where fractional recall comes from;
* damage confined to **one principal**, which is the permission-cliff case.
"""

from __future__ import annotations

import json
from collections.abc import Collection, Mapping, Sequence
from pathlib import Path

import pytest

from company_brain.eval.baseline import (
    SEEDED_TOLERANCE,
    compare,
    load_baseline,
    write_baseline,
)
from company_brain.eval.harness import EvalReport, QuestionResult, summarize
from company_brain.eval.questions import (
    GOLDENS,
    KNOWN_FAMILIES,
    Golden,
    QuestionClass,
    source_of,
    visible_evidence,
)

PRINCIPALS = ("ceo", "support-lead", "eng-ic", "contractor")
LEAKED_NODE = "documents/slack/leadership-comp/slack-thread-2024-01-08-aaaaaa"


def golden(question_id: str) -> Golden:
    return next(g for g in GOLDENS if g.id == question_id)


def ids_of(qclass: QuestionClass, limit: int | None = None) -> list[str]:
    found = [g.id for g in GOLDENS if g.qclass is qclass]
    return found[:limit] if limit is not None else found


SEEDED_IDS = [g.id for g in GOLDENS if g.seeded]
# A question resting on three kinds of evidence — a process page, its runbook
# and its PDF policy. Losing one of the three is the fractional-recall case.
THREE_KINDS = next(g for g in GOLDENS if len(g.evidence) == 3)


def answer(
    question: Golden,
    principal: str,
    *,
    kinds_found: int | None = None,
    leaked: tuple[str, ...] = (),
    error: str = "",
) -> QuestionResult:
    """One question, answered by one principal.

    `kinds_found` is how many of the evidence kinds this principal can see were
    actually retrieved; `None` means all of them.
    """
    expected = visible_evidence(question, principal)
    matched = expected if kinds_found is None else expected[:kinds_found]
    return QuestionResult(
        question_id=question.id,
        principal=principal,
        qclass=question.qclass.value,
        seeded=question.seeded,
        expected=expected,
        retrieved=matched,
        matched=matched,
        cited=(),
        refused=not expected,
        leaked=leaked,
        error=error,
    )


def run(
    *,
    missed: Collection[str] = (),
    partial: Mapping[str, int] | None = None,
    only_for: str | None = None,
    dropped: Collection[str] = (),
    leaks: Collection[str] = (),
    errors: Collection[str] = (),
    goldens: Sequence[Golden] = GOLDENS,
    principals: tuple[str, ...] = PRINCIPALS,
) -> EvalReport:
    """A full run of the golden set, damaged in the named ways.

    With no arguments this is a perfect run: every principal retrieves every
    evidence kind they are allowed to see. `only_for` confines the damage to a
    single principal, which is how a permission cliff shows up.
    """
    partial = dict(partial or {})
    results: list[QuestionResult] = []
    for principal in principals:
        for question in goldens:
            if question.id in dropped:
                continue
            damaged = only_for is None or principal == only_for
            kinds = None
            if damaged and question.id in missed:
                kinds = 0
            elif damaged and question.id in partial:
                kinds = partial[question.id]
            results.append(
                answer(
                    question,
                    principal,
                    kinds_found=kinds,
                    leaked=(LEAKED_NODE,) if question.id in leaks else (),
                    error="UncitedAnswerError" if question.id in errors else "",
                )
            )
    return EvalReport(
        k=10,
        principals=principals,
        synthesizer="extractive-offline",
        results=results,
    )


def paths(report: EvalReport, baseline: EvalReport) -> set[str]:
    return {r.path for r in compare(report, baseline.to_json())}


class TestScoringOnRealQuestions:
    def test_recall_counts_evidence_kinds_not_documents(self) -> None:
        assert len(THREE_KINDS.evidence) == 3
        two_of_three = answer(THREE_KINDS, "ceo", kinds_found=2)
        assert two_of_three.recall == pytest.approx(2 / 3)
        assert two_of_three.hit is True

    def test_a_principal_who_cannot_see_the_evidence_is_not_scored_for_recall(self) -> None:
        """The contractor holds only the general channel, so every answerable
        golden is blind to them — and a blind question is a refusal question,
        not a zero."""
        blind = answer(golden(SEEDED_IDS[0]), "contractor")
        assert blind.expected == ()
        assert blind.graded_for_recall is False
        assert blind.should_refuse is True
        assert summarize([blind]).graded == 0

    def test_a_perfect_run_scores_one_and_grades_only_who_can_see(self) -> None:
        report = run()
        assert report.overall.recall_at_k == 1.0
        assert report.by_principal["contractor"].graded == 0
        assert report.by_principal["ceo"].graded > 0
        assert not report.leaks


class TestTheAggregateGate:
    def test_questions_that_stop_working_are_caught(self) -> None:
        before = run()
        after = run(missed=ids_of(QuestionClass.FACTUAL, 5))
        assert "overall.recall_at_k" in paths(after, before)

    def test_one_question_losing_one_of_its_three_evidence_kinds_is_tolerated(self) -> None:
        """The 0.02 slack exists for exactly this: a change that costs a third
        of one question's evidence and presumably bought something elsewhere.
        Anything larger blocks the build."""
        before = run()
        after = run(partial={THREE_KINDS.id: 2})
        assert after.overall.recall_at_k < before.overall.recall_at_k
        assert not paths(after, before)


class TestTheNarrowerRules:
    def test_a_class_regression_the_aggregate_cannot_see_is_caught(self) -> None:
        """Factual falls exactly as far as temporal rises, so overall recall is
        identical on both sides. Without per-class gating this is invisible."""
        temporal = ids_of(QuestionClass.TEMPORAL)
        factual = ids_of(QuestionClass.FACTUAL, len(temporal))
        before = run(missed=temporal)
        after = run(missed=factual)

        assert before.overall.recall_at_k == after.overall.recall_at_k
        regressions = paths(after, before)
        assert "by_class.factual.recall_at_k" in regressions
        assert "overall.recall_at_k" not in regressions

    def test_a_regression_confined_to_one_principal_is_caught(self) -> None:
        """The permission cliff, inverted: the CEO stops finding things only
        they can reach. Three questions out of 110 is under the aggregate
        tolerance, so only the per-principal view fails."""
        broken = [
            ids_of(QuestionClass.FACTUAL, 1)[0],
            ids_of(QuestionClass.OWNERSHIP, 1)[0],
            ids_of(QuestionClass.SYSTEMIC, 1)[0],
        ]
        before = run()
        after = run(missed=broken, only_for="ceo")

        regressions = paths(after, before)
        assert "by_principal.ceo.recall_at_k" in regressions
        assert "overall.recall_at_k" not in regressions
        assert not any(p.startswith("by_principal.eng-ic") for p in regressions)

    def test_an_m1_golden_regressing_is_caught_where_the_aggregate_tolerates_it(
        self,
    ) -> None:
        """ROADMAP M4: no regression against the M1 goldens. One of the ten
        breaking is 1/110 of the run — well inside the aggregate tolerance — and
        must still fail.

        Note what this does *not* prove: with only ten M1 goldens the smallest
        possible drop is 0.1, so `SEEDED_TOLERANCE` of 0.0 and of 0.02 would
        behave identically here. The zero is what keeps that true if the seeded
        set ever grows.
        """
        assert SEEDED_TOLERANCE == 0.0
        before = run()
        after = run(missed=[SEEDED_IDS[0]], only_for="ceo")

        regressions = paths(after, before)
        assert "seeded.recall_at_k" in regressions
        assert "overall.recall_at_k" not in regressions


class TestWhatIsNeverTradeable:
    def test_a_new_leak_fails_however_much_recall_improves(self) -> None:
        before = run(missed=ids_of(QuestionClass.FACTUAL, 10))
        after = run(leaks=[SEEDED_IDS[0]])

        assert after.overall.recall_at_k > before.overall.recall_at_k
        assert "overall.leaks" in paths(after, before)

    def test_a_new_validator_error_is_caught(self) -> None:
        before = run()
        after = run(errors=[SEEDED_IDS[0]])
        assert "overall.errors" in paths(after, before)

    def test_deleting_the_questions_that_fail_does_not_buy_a_better_score(self) -> None:
        failing = ids_of(QuestionClass.SYSTEMIC, 5)
        before = run(missed=failing)
        after = run(dropped=failing)

        assert after.overall.recall_at_k > before.overall.recall_at_k
        assert {"overall.questions", "overall.graded"} <= paths(after, before)

    def test_dropping_a_principal_entirely_is_caught(self) -> None:
        before = run()
        after = run(principals=("ceo", "support-lead", "eng-ic"))
        assert "by_principal.contractor (missing)" in paths(after, before)

    def test_a_question_class_disappearing_is_caught(self) -> None:
        before = run()
        after = run(dropped=ids_of(QuestionClass.UNANSWERABLE))
        regressions = paths(after, before)
        assert "by_class.unanswerable.questions" in regressions


class TestTheCommittedBaseline:
    def test_it_describes_the_current_golden_set(self) -> None:
        baseline = load_baseline()
        assert baseline["by_class"].keys() == {q.value for q in QuestionClass}
        assert baseline["principals"] == list(PRINCIPALS)
        assert baseline["overall"]["questions"] == len(GOLDENS) * len(PRINCIPALS)

    def test_the_committed_baseline_admits_a_perfect_run(self) -> None:
        """Sanity on the direction of the comparison: the pipeline getting
        everything right must never read as a regression."""
        assert not compare(run(), load_baseline())

    def test_writing_it_round_trips(self, tmp_path: Path) -> None:
        report = run()
        path = tmp_path / "baseline.json"
        write_baseline(report, path)
        assert json.loads(path.read_text()) == report.to_json()
        assert not compare(report, load_baseline(path))

    def test_a_missing_baseline_says_how_to_make_one(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="update-baseline"):
            load_baseline(tmp_path / "nope.json")


class TestSourceFamilies:
    """The leak check derives a node's source family from its ID. A wrong
    derivation makes the check silently pass, so it is pinned here."""

    @pytest.mark.parametrize(
        ("node_id", "family"),
        [
            (LEAKED_NODE, "slack:leadership-comp"),
            ("documents/slack/general/slack-thread-2024-01-08-aaaaaa", "slack:general"),
            ("documents/email/weekly-escalation-digest-1-7decc7", "email"),
            ("documents/docs/processes/vendor-renewal-f54195", "docs"),
            ("documents/pdf/vendor-renewal-policy-9c25a7", "docs"),
            ("people/sam-kaur", "docs"),
            ("processes/vendor-renewal", "docs"),
        ],
    )
    def test_a_node_id_maps_to_its_family(self, node_id: str, family: str) -> None:
        assert source_of(node_id) == family
        assert family in KNOWN_FAMILIES

    def test_every_golden_names_a_family_that_exists(self) -> None:
        # Enforced at import time in `questions._build`; asserted here so the
        # reason it matters is written down next to the check.
        for question in GOLDENS:
            for pattern in question.evidence:
                assert source_of(pattern) in KNOWN_FAMILIES, f"{question.id}: {pattern}"
