"""The retrieval-quality evaluation harness.

M4's scope is a list of retrieval-quality claims — process modelling, handoff
analysis, systemic queries, evidence-grade synthesis. None of them is verifiable
by a unit test, and all of them can drift silently. So the harness lands before
the features it grades, and every M4 change is measured against a committed
baseline (:mod:`company_brain.eval.baseline`).

Three things make it more than a smoke test:

* **Ground truth is derived from the corpus generator's own tables**, not typed
  out by hand, so a golden question cannot rot away from the corpus it grades.
  ``tests/acceptance/test_m4_eval.py`` asserts every expected pattern still
  resolves to a real node.
* **Every question is run once per principal**, and recall is measured against
  the evidence *that principal can see*. A principal-specific drop is then a
  retrieval bug, not a permissions artefact — which is the whole point of
  tracking recall per principal class rather than in aggregate.
* **Leaks are checked on every answer, not on a canary list.** Each retrieved
  and cited node's source family is derived from its ID and checked against what
  the principal is allowed to see, so all 440 question/principal pairs are leak
  tests rather than the four the acceptance suite plants by hand.
"""

from __future__ import annotations

from company_brain.eval.harness import (
    EvalReport,
    Metrics,
    QuestionResult,
    run_eval,
)
from company_brain.eval.questions import (
    GOLDENS,
    VISIBLE_SOURCES,
    Golden,
    QuestionClass,
    source_of,
    visible_evidence,
)

__all__ = [
    "GOLDENS",
    "VISIBLE_SOURCES",
    "EvalReport",
    "Golden",
    "Metrics",
    "QuestionClass",
    "QuestionResult",
    "run_eval",
    "source_of",
    "visible_evidence",
]
