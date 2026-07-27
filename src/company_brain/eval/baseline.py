"""The committed baseline and the regression gate.

A quality number with nothing to compare it to is decoration. `baseline.json`
records what the pipeline scored when it was last deliberately changed, and CI
fails the build when a metric falls below it — so retrieval quality drifts
loudly instead of silently, which is the reason the harness lands before the
features it grades.

Two tolerances, on purpose:

* ``TOLERANCE`` (0.02) for the aggregate and per-class metrics. The pipeline is
  deterministic, so any movement is real; the slack is for changes that trade a
  point of recall on one class for more elsewhere and should be reviewed rather
  than blocked.
* **Zero** for the ten M1 goldens. ROADMAP M4 says "no regression versus M3 on
  the M1 goldens", and the honest reading of that is exactly zero.

Leaks gate at zero unconditionally and are not a metric you may trade against.
Updating the baseline is a deliberate act (`cb eval --update-baseline`) that
produces a reviewed diff, in the same spirit as refreshing the extraction cache.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from company_brain.eval.harness import EvalReport

BASELINE_PATH: Final = Path(__file__).with_name("baseline.json")
TOLERANCE: Final = 0.02
SEEDED_TOLERANCE: Final = 0.0

# Metrics where a smaller number is a regression.
_HIGHER_IS_BETTER: Final = ("recall_at_k", "hit_rate", "refusal_rate")
# Metrics where a larger number is a regression.
_LOWER_IS_BETTER: Final = ("leaks", "errors")
# Counts that must not shrink. Dropping questions is the cheapest way to raise
# every rate above, so the denominators are gated too.
#
# This is also what handles a rate over an *empty* denominator. `summarize`
# reports those as 0.0, so two absences compare equal and never trip the rate
# check on their own — it is the collapse of `graded` from N to 0 that fails,
# which is the thing actually worth failing on.
_COUNTS: Final = ("questions", "graded")


@dataclass(frozen=True, slots=True)
class Regression:
    path: str
    baseline: float
    current: float
    tolerance: float

    def __str__(self) -> str:
        return (
            f"{self.path}: {self.current:.4f} vs baseline {self.baseline:.4f} "
            f"(tolerance {self.tolerance:.4f})"
        )


def load_baseline(path: Path = BASELINE_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"no baseline at {path}; record one with `cb eval --update-baseline`"
        )
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"malformed baseline at {path}")
    return data


def write_baseline(report: EvalReport, path: Path = BASELINE_PATH) -> None:
    path.write_text(json.dumps(report.to_json(), indent=2, sort_keys=True) + "\n")


def _walk(node: Any, prefix: str = "") -> list[tuple[str, dict[str, Any]]]:
    """Every metrics block in a report, keyed by its dotted path."""
    out: list[tuple[str, dict[str, Any]]] = []
    if isinstance(node, dict):
        if "recall_at_k" in node:
            out.append((prefix, node))
        else:
            for key, value in sorted(node.items()):
                if isinstance(value, dict):
                    out.extend(_walk(value, f"{prefix}.{key}" if prefix else str(key)))
    return out


def compare(
    report: EvalReport,
    baseline: dict[str, Any],
    *,
    tolerance: float = TOLERANCE,
) -> list[Regression]:
    """Every metric that moved the wrong way. Empty means the gate passes.

    A metrics block present in the baseline but missing from the report is a
    regression too — deleting questions is the cheapest way to raise a score,
    and it should not be a quiet one.
    """
    current = report.to_json()
    found = dict(_walk(current))
    regressions: list[Regression] = []

    for path, before in _walk(baseline):
        after = found.get(path)
        if after is None:
            regressions.append(Regression(f"{path} (missing)", 1.0, 0.0, 0.0))
            continue
        seeded = path == "seeded" or path.startswith("seeded.")
        limit = SEEDED_TOLERANCE if seeded else tolerance
        for metric in _HIGHER_IS_BETTER:
            base, now = float(before[metric]), float(after[metric])
            if now < base - limit:
                regressions.append(Regression(f"{path}.{metric}", base, now, limit))
        for metric in _LOWER_IS_BETTER:
            base, now = float(before[metric]), float(after[metric])
            if now > base:
                regressions.append(Regression(f"{path}.{metric}", base, now, 0.0))
        for metric in _COUNTS:
            base, now = float(before[metric]), float(after[metric])
            if now < base:
                regressions.append(Regression(f"{path}.{metric}", base, now, 0.0))

    return regressions
