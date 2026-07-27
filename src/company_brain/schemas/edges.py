"""Typed edges and the gate policy that decides which ones enter the graph.

Every edge carries provenance, confidence, evidence, and status (invariant 10).
Only ``accepted`` edges are traversed at query time — a proposed edge is visible
in the markdown and in the review queue, and invisible to retrieval.

The gate policy is per-predicate rather than one global confidence threshold,
because the predicates differ enormously in both extractability and blast radius
(docs/ARCHITECTURE.md §11).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Predicate(StrEnum):
    AUTHORED_BY = "authored_by"
    MENTIONS = "mentions"
    MENTIONS_UNRESOLVED = "mentions_unresolved"
    OWNS = "owns"
    DEPENDS_ON = "depends_on"
    HANDOFF_TO = "handoff_to"
    SUPERSEDES = "supersedes"
    OPERATED_BY = "operated_by"
    # Internal bookkeeping, not extracted from content.
    SAME_AS = "same_as"
    REDIRECTS_TO = "redirects_to"


class Provenance(StrEnum):
    STRUCTURAL = "structural"  # from source metadata; not inferred
    LLM = "llm"
    HUMAN = "human"


class EdgeStatus(StrEnum):
    ACCEPTED = "accepted"
    PROPOSED = "proposed"
    REJECTED = "rejected"
    STALE = "stale"  # evidence span no longer exists after an upstream edit


class Evidence(BaseModel):
    """Where a claim came from.

    ``span`` is a half-open ``[start, end)`` character range into the *normalized
    markdown body* of ``node`` — not the original source bytes, which we may not
    retain. ``self`` means the node carrying the edge.
    """

    model_config = ConfigDict(frozen=True)

    node: str = "self"
    span: tuple[int, int] | None = None
    quote: str | None = None

    @model_validator(mode="after")
    def _span_is_sane(self) -> Self:
        if self.span is not None:
            start, end = self.span
            if start < 0 or end <= start:
                raise ValueError(f"span must be a non-empty [start, end), got {self.span}")
        return self


class Edge(BaseModel):
    """One typed relation. Serialized into the frontmatter ``relations`` block."""

    model_config = ConfigDict(frozen=True)

    predicate: Predicate
    object: str
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: Provenance
    status: EdgeStatus
    evidence: tuple[Evidence, ...] = ()

    @model_validator(mode="after")
    def _llm_edges_cite(self) -> Self:
        # An LLM-derived edge with no evidence cannot be reviewed, which makes the
        # §11 gate unenforceable. Reject at construction rather than at review time.
        if self.provenance is Provenance.LLM and not self.evidence:
            raise ValueError(f"llm-derived {self.predicate} edge must carry evidence")
        return self

    def sort_key(self) -> tuple[str, str]:
        """Deterministic ordering for canonical emit (invariant 3)."""
        return (str(self.predicate), self.object)


class Gate(BaseModel):
    """Policy for one predicate."""

    model_config = ConfigDict(frozen=True)

    auto_accept_above: float | None  # None => never auto-accept from an LLM
    min_evidence: int = 1
    distinct_source_docs: int = 1


# docs/ARCHITECTURE.md §11. Structural edges bypass this table entirely — they
# come from source metadata, not inference.
GATES: Final[dict[Predicate, Gate]] = {
    Predicate.AUTHORED_BY: Gate(auto_accept_above=0.0),
    Predicate.MENTIONS: Gate(auto_accept_above=0.85),
    Predicate.MENTIONS_UNRESOLVED: Gate(auto_accept_above=0.0),
    Predicate.SUPERSEDES: Gate(auto_accept_above=None),
    Predicate.DEPENDS_ON: Gate(auto_accept_above=None),
    Predicate.HANDOFF_TO: Gate(auto_accept_above=None),
    # Highest blast radius in the whole taxonomy. "Sam was quoted about the
    # renewal in four threads" is not "Sam owns vendor renewals", and an answer
    # that confuses the two arrives with four real citations attached.
    Predicate.OWNS: Gate(auto_accept_above=None, min_evidence=2, distinct_source_docs=2),
    Predicate.OPERATED_BY: Gate(auto_accept_above=None),
    Predicate.SAME_AS: Gate(auto_accept_above=None),
    Predicate.REDIRECTS_TO: Gate(auto_accept_above=0.0),
}


def decide_status(
    predicate: Predicate,
    confidence: float,
    provenance: Provenance,
    evidence: tuple[Evidence, ...],
) -> EdgeStatus:
    """Apply the gate. Human and structural edges are accepted as given."""
    if provenance in (Provenance.HUMAN, Provenance.STRUCTURAL):
        return EdgeStatus.ACCEPTED

    gate = GATES[predicate]
    if gate.auto_accept_above is None:
        return EdgeStatus.PROPOSED
    if confidence < gate.auto_accept_above:
        return EdgeStatus.PROPOSED
    if len(evidence) < gate.min_evidence:
        return EdgeStatus.PROPOSED
    distinct = {e.node for e in evidence}
    if len(distinct) < gate.distinct_source_docs:
        return EdgeStatus.PROPOSED
    return EdgeStatus.ACCEPTED
