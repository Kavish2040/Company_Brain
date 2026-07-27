"""Scored matching over blocked candidates.

The requirement this module answers is legibility: a reviewer is being asked to
merge two records in someone's company, and "0.83" is not a reason. So a score
here is never one number — it is a table of named components, each with its own
raw value, weight and contribution, and the table is what gets written into the
proposal a human reads.

Three rules shape the arithmetic:

* **Absent context is not evidence against.** A freshly created duplicate has no
  documents, so co-occurrence, channel and temporal features have nothing to
  say about it. Scoring those as 0 and dividing by the full weight quietly
  punishes exactly the records most likely to be duplicates. Inapplicable
  components leave the denominator instead.
* **A veto beats every positive signal.** Two distinct accounts in one corporate
  directory means two people, however similar the names look. §10.2's warning is
  that co-occurrence makes Sam-Kaur-versus-Sam-Kelly *worse*, so a purely
  additive score cannot be the last word.
* **No identity key, no high confidence.** §10.2 again: for people, a name-only
  match is worth a reviewer's glance and is never worth certainty. The ceiling
  is applied to the score, not to the review decision — the pair still gets
  proposed, it just cannot arrive claiming to be sure.

Weights and thresholds are plain dataclass fields with defaults, so tuning is a
constructor argument rather than an edit to this file.
"""

from __future__ import annotations

from dataclasses import dataclass

from company_brain.resolve.keys import (
    dice,
    fold,
    identity_surface,
    is_email,
    jaccard,
    name_tokens,
)
from company_brain.resolve.profiles import EntityProfile
from company_brain.schemas.nodes import NodeType

# Declared order. Summation happens in this order so the floating-point result
# is a function of the declared sequence and not of dict or set iteration.
COMPONENT_ORDER: tuple[str, ...] = (
    "identity_key",
    "name_similarity",
    "alias_overlap",
    "colleague_overlap",
    "channel_overlap",
    "temporal_overlap",
)


@dataclass(frozen=True, slots=True)
class Weights:
    """Relative pull of each component. Tunable; only the ratios matter."""

    identity_key: float = 0.28
    name_similarity: float = 0.30
    alias_overlap: float = 0.22
    colleague_overlap: float = 0.08
    channel_overlap: float = 0.07
    temporal_overlap: float = 0.05

    def of(self, name: str) -> float:
        return float(getattr(self, name))


@dataclass(frozen=True, slots=True)
class Policy:
    """Where the thresholds sit, and which types they bind on."""

    propose_above: float = 0.55
    # A Person or Account match with no shared identity key cannot exceed this,
    # however well the strings line up. Below `propose_above` would disable
    # name-only matching entirely; the intent is a ceiling, not a mute button.
    cap_without_identity_key: float = 0.70
    capped_types: tuple[NodeType, ...] = (NodeType.PERSON, NodeType.ACCOUNT)


@dataclass(frozen=True, slots=True)
class Component:
    """One named signal. ``applicable`` is False when neither side has the data
    the component reads — distinct from a real 0.0, which is disagreement."""

    name: str
    raw: float
    weight: float
    applicable: bool
    detail: str = ""

    @property
    def contribution(self) -> float:
        return round(self.raw * self.weight, 6) if self.applicable else 0.0


@dataclass(frozen=True, slots=True)
class ScoreCard:
    left: str
    right: str
    components: tuple[Component, ...]
    score: float
    veto: str | None = None
    capped_from: float | None = None

    @property
    def has_identity_key(self) -> bool:
        return any(
            c.name == "identity_key" and c.applicable and c.raw > 0 for c in self.components
        )

    def table(self) -> str:
        """The reviewer-facing breakdown, as a markdown table.

        This is the deliverable, not a debug aid: it is what makes the match
        arguable rather than merely reported.
        """
        rows = [
            "| component | raw | weight | contribution |",
            "| --- | ---: | ---: | ---: |",
        ]
        for component in self.components:
            raw = f"{component.raw:.4f}" if component.applicable else "n/a"
            contribution = (
                f"{component.contribution:.4f}" if component.applicable else "excluded"
            )
            detail = f" {component.detail}" if component.detail else ""
            weight = f"{component.weight:.2f}"
            rows.append(f"| {component.name}{detail} | {raw} | {weight} | {contribution} |")
        rows.append(f"| **score** | | | **{self.score:.4f}** |")
        if self.capped_from is not None:
            rows.append(
                f"| _capped from {self.capped_from:.4f}_ | | | "
                f"_no shared identity key (§10.2)_ |"
            )
        if self.veto is not None:
            rows.append(f"| _vetoed_ | | | _{self.veto}_ |")
        return "\n".join(rows)


def _name_surfaces(profile: EntityProfile) -> tuple[str, ...]:
    """Surfaces that are names rather than addresses, normalized and sorted."""
    folded = {" ".join(name_tokens(s)) for s in profile.surfaces if not is_email(s)}
    return tuple(sorted(f for f in folded if f))


def _all_surfaces(profile: EntityProfile) -> tuple[str, ...]:
    folded = {fold(s) for s in profile.surfaces}
    return tuple(sorted(f for f in folded if f))


def _identity_component(left: EntityProfile, right: EntityProfile, weight: float) -> Component:
    applicable = bool(left.identity_keys) and bool(right.identity_keys)
    shared = sorted(set(left.identity_keys) & set(right.identity_keys))
    # The address as written, not the normalized match key — see
    # `keys.identity_surface`.
    detail = f"({identity_surface(left.surfaces, shared[0])})" if shared else ""
    return Component(
        name="identity_key",
        raw=1.0 if shared else 0.0,
        weight=weight,
        applicable=applicable,
        detail=detail,
    )


def _name_component(left: EntityProfile, right: EntityProfile, weight: float) -> Component:
    mine, theirs = _name_surfaces(left), _name_surfaces(right)
    if not mine or not theirs:
        return Component("name_similarity", 0.0, weight, applicable=False)
    # Best pair, not title-to-title: the duplicate record is the one whose
    # title is unhelpful, and its full name usually survives only as an alias.
    best = max(dice(a, b) for a in mine for b in theirs)
    return Component("name_similarity", best, weight, applicable=True)


def _alias_component(left: EntityProfile, right: EntityProfile, weight: float) -> Component:
    mine, theirs = _all_surfaces(left), _all_surfaces(right)
    if not mine or not theirs:
        return Component("alias_overlap", 0.0, weight, applicable=False)
    return Component("alias_overlap", jaccard(mine, theirs), weight, applicable=True)


def _colleague_component(left: EntityProfile, right: EntityProfile, weight: float) -> Component:
    # Each side's view of the other is removed: two records for one person
    # co-occur with each other by construction, and counting that would be the
    # feature scoring its own hypothesis.
    mine = tuple(n for n in left.neighbours if n != right.node_id)
    theirs = tuple(n for n in right.neighbours if n != left.node_id)
    if not mine or not theirs:
        return Component("colleague_overlap", 0.0, weight, applicable=False)
    return Component("colleague_overlap", jaccard(mine, theirs), weight, applicable=True)


def _channel_component(left: EntityProfile, right: EntityProfile, weight: float) -> Component:
    if not left.channels or not right.channels:
        return Component("channel_overlap", 0.0, weight, applicable=False)
    return Component("channel_overlap", jaccard(left.channels, right.channels), weight, True)


def _temporal_component(left: EntityProfile, right: EntityProfile, weight: float) -> Component:
    if None in (left.first_seen, left.last_seen, right.first_seen, right.last_seen):
        return Component("temporal_overlap", 0.0, weight, applicable=False)
    assert left.first_seen and left.last_seen and right.first_seen and right.last_seen
    start = max(left.first_seen, right.first_seen)
    end = min(left.last_seen, right.last_seen)
    span_start = min(left.first_seen, right.first_seen)
    span_end = max(left.last_seen, right.last_seen)
    span = (span_end - span_start).total_seconds()
    if span <= 0:
        return Component("temporal_overlap", 1.0, weight, applicable=True)
    overlap = max(0.0, (end - start).total_seconds())
    return Component("temporal_overlap", round(overlap / span, 6), weight, applicable=True)


def score_pair(
    left: EntityProfile,
    right: EntityProfile,
    *,
    weights: Weights | None = None,
    policy: Policy | None = None,
    veto: str | None = None,
) -> ScoreCard:
    """Score one candidate pair into a legible card.

    ``veto`` is passed in rather than computed here so the caller decides which
    negative signals it trusts; `keys.identity_conflict` supplies the one this
    codebase ships with.
    """
    w = weights or Weights()
    p = policy or Policy()
    components = (
        _identity_component(left, right, w.of("identity_key")),
        _name_component(left, right, w.of("name_similarity")),
        _alias_component(left, right, w.of("alias_overlap")),
        _colleague_component(left, right, w.of("colleague_overlap")),
        _channel_component(left, right, w.of("channel_overlap")),
        _temporal_component(left, right, w.of("temporal_overlap")),
    )
    assert tuple(c.name for c in components) == COMPONENT_ORDER

    if veto is not None:
        return ScoreCard(left.node_id, right.node_id, components, score=0.0, veto=veto)

    applicable = tuple(c for c in components if c.applicable)
    denominator = round(sum(c.weight for c in applicable), 6)
    if denominator <= 0:
        return ScoreCard(left.node_id, right.node_id, components, score=0.0)
    numerator = round(sum(c.contribution for c in applicable), 6)
    score = round(numerator / denominator, 6)

    capped_from: float | None = None
    identity = components[0]
    if (
        left.node_type in p.capped_types
        and not (identity.applicable and identity.raw > 0)
        and score > p.cap_without_identity_key
    ):
        capped_from, score = score, p.cap_without_identity_key

    return ScoreCard(
        left.node_id, right.node_id, components, score=score, capped_from=capped_from
    )
