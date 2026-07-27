"""Running the golden set and scoring it.

The unit of measurement is a (question, principal) pair, not a question. Four
principals over 110 goldens is 440 graded retrievals, and the per-principal
breakdown is what turns "recall fell" into either "retrieval regressed" or
"someone lost a grant" — two failures that look identical in an aggregate score.

Scoring rules, in one place because they are the harness's whole contract:

* **Recall** counts evidence *kinds* found, over the kinds the principal can
  reach (:func:`questions.visible_evidence`). A question whose evidence is
  entirely invisible to the principal is not scored for recall at all — it moves
  into the refusal bucket, where the correct behaviour is to say so.
* **Refusal** is graded on the questions where refusing is right: the
  ``unanswerable`` class, plus every question a principal is blind to. It is a
  score, not a failure mode.
* **A leak is never a score.** Any retrieved or cited node from a source family
  the principal cannot see is counted separately and gates the suite at zero.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from company_brain.eval.questions import (
    GOLDENS,
    VISIBLE_SOURCES,
    Golden,
    QuestionClass,
    source_of,
    visible_evidence,
)
from company_brain.retrieve.hybrid import HybridRetriever
from company_brain.synthesize.answer import (
    CitationLeakError,
    Synthesizer,
    UncitedAnswerError,
    validate,
)

if TYPE_CHECKING:  # pragma: no cover - import cycle only matters to type checkers
    from company_brain.app import App

DEFAULT_K = 10
DEFAULT_PRINCIPALS: tuple[str, ...] = ("ceo", "support-lead", "eng-ic", "contractor")


@dataclass(frozen=True, slots=True)
class QuestionResult:
    question_id: str
    principal: str
    qclass: str
    seeded: bool
    expected: tuple[str, ...]
    retrieved: tuple[str, ...]
    matched: tuple[str, ...]
    cited: tuple[str, ...]
    refused: bool
    leaked: tuple[str, ...]
    error: str = ""

    @property
    def graded_for_recall(self) -> bool:
        return bool(self.expected)

    @property
    def recall(self) -> float:
        return len(self.matched) / len(self.expected) if self.expected else 0.0

    @property
    def hit(self) -> bool:
        return bool(self.matched)

    @property
    def should_refuse(self) -> bool:
        """No visible evidence exists, so 'insufficient evidence' is the answer.

        Covers both the unanswerable class and the permission cliff: a
        contractor asked who owns vendor renewals is in exactly the position of
        someone asked an unanswerable question, and should behave the same way.
        """
        return not self.expected


@dataclass(frozen=True, slots=True)
class Metrics:
    questions: int
    graded: int
    recall_at_k: float
    hit_rate: float
    refusal_expected: int
    refusal_rate: float
    leaks: int
    errors: int

    def to_json(self) -> dict[str, Any]:
        return {
            "questions": self.questions,
            "graded": self.graded,
            "recall_at_k": self.recall_at_k,
            "hit_rate": self.hit_rate,
            "refusal_expected": self.refusal_expected,
            "refusal_rate": self.refusal_rate,
            "leaks": self.leaks,
            "errors": self.errors,
        }


def _round(value: float) -> float:
    # Baselines are committed and diffed; four places is well inside the noise
    # floor of a deterministic pipeline and keeps the diff readable.
    return round(value, 4)


def summarize(results: Sequence[QuestionResult]) -> Metrics:
    graded = [r for r in results if r.graded_for_recall]
    refusable = [r for r in results if r.should_refuse]
    return Metrics(
        questions=len(results),
        graded=len(graded),
        recall_at_k=_round(sum(r.recall for r in graded) / len(graded)) if graded else 0.0,
        hit_rate=_round(sum(1 for r in graded if r.hit) / len(graded)) if graded else 0.0,
        refusal_expected=len(refusable),
        refusal_rate=(
            _round(sum(1 for r in refusable if r.refused) / len(refusable))
            if refusable
            else 0.0
        ),
        leaks=sum(len(r.leaked) for r in results),
        errors=sum(1 for r in results if r.error),
    )


@dataclass(slots=True)
class EvalReport:
    k: int
    principals: tuple[str, ...]
    synthesizer: str
    results: list[QuestionResult] = field(default_factory=list)

    @property
    def overall(self) -> Metrics:
        return summarize(self.results)

    @property
    def by_class(self) -> dict[str, Metrics]:
        return {
            qclass.value: summarize([r for r in self.results if r.qclass == qclass.value])
            for qclass in QuestionClass
        }

    @property
    def by_principal(self) -> dict[str, Metrics]:
        return {
            principal: summarize([r for r in self.results if r.principal == principal])
            for principal in self.principals
        }

    @property
    def by_principal_class(self) -> dict[str, dict[str, Metrics]]:
        """Recall@k per principal *per question class*.

        The cell that matters is the one where a principal can see the evidence
        and still does not retrieve it; the aggregate hides that behind the
        principals who legitimately see less.
        """
        return {
            principal: {
                qclass.value: summarize(
                    [
                        r
                        for r in self.results
                        if r.principal == principal and r.qclass == qclass.value
                    ]
                )
                for qclass in QuestionClass
            }
            for principal in self.principals
        }

    @property
    def seeded(self) -> Metrics:
        """The M1 goldens, as answered by the CEO — the M1 acceptance condition."""
        return summarize(
            [r for r in self.results if r.seeded and r.principal == "ceo"],
        )

    @property
    def leaks(self) -> list[QuestionResult]:
        return [r for r in self.results if r.leaked]

    def to_json(self) -> dict[str, Any]:
        return {
            "k": self.k,
            "principals": list(self.principals),
            "synthesizer": self.synthesizer,
            "overall": self.overall.to_json(),
            "seeded": self.seeded.to_json(),
            "by_class": {k: v.to_json() for k, v in sorted(self.by_class.items())},
            "by_principal": {k: v.to_json() for k, v in sorted(self.by_principal.items())},
            "by_principal_class": {
                principal: {k: v.to_json() for k, v in sorted(classes.items())}
                for principal, classes in sorted(self.by_principal_class.items())
            },
        }


def _leaked(node_ids: Iterable[str], principal: str) -> tuple[str, ...]:
    allowed = VISIBLE_SOURCES[principal]
    return tuple(sorted({n for n in node_ids if source_of(n) not in allowed}))


def run_one(
    app: App,
    golden: Golden,
    principal: str,
    *,
    k: int,
    synthesizer: Synthesizer,
) -> QuestionResult:
    access = app.access(app.principal(principal))
    retrieval = HybridRetriever(app.index, access).retrieve(golden.question, limit=k)
    top = tuple(n.node_id for n in retrieval.nodes[:k])

    expected = visible_evidence(golden, principal)
    matched = tuple(p for p in expected if any(p in node_id for node_id in top))

    answer = synthesizer.synthesize(golden.question, retrieval, app.index)
    cited = tuple(c.node_id for c in answer.citations)

    error = ""
    try:
        validate(answer, retrieval, access, app.index)
    except (CitationLeakError, UncitedAnswerError) as exc:
        error = type(exc).__name__

    # Leaks are checked over everything retrieval surfaced, not just the top k:
    # a node the principal cannot see has already crossed the boundary by the
    # time ranking decides whether to show it.
    return QuestionResult(
        question_id=golden.id,
        principal=principal,
        qclass=golden.qclass.value,
        seeded=golden.seeded,
        expected=expected,
        retrieved=top,
        matched=matched,
        cited=cited,
        refused=answer.insufficient_evidence,
        leaked=_leaked([n.node_id for n in retrieval.nodes] + list(cited), principal),
        error=error,
    )


def run_eval(
    app: App,
    *,
    goldens: Sequence[Golden] = GOLDENS,
    principals: Sequence[str] = DEFAULT_PRINCIPALS,
    k: int = DEFAULT_K,
    synthesizer: Synthesizer | None = None,
) -> EvalReport:
    """Run every golden as every principal. Deterministic, given a fixed store.

    The synthesizer defaults to whatever the composition root configured, so a
    CI run grades the offline extractive path and an online run grades Claude —
    both against the same goldens rather than two different bars.
    """
    engine = synthesizer if synthesizer is not None else app.providers.synthesizer()
    report = EvalReport(k=k, principals=tuple(principals), synthesizer=engine.name)
    for principal in principals:
        for golden in goldens:
            report.results.append(run_one(app, golden, principal, k=k, synthesizer=engine))
    return report
