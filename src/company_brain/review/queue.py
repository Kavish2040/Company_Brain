"""The review queue.

Two things land here: agent writes (invariant 9) and extraction output the §11
gates refused to auto-accept. The second is the larger volume by far — at 201
documents every `owns` edge is already proposed, because `owns` has no
auto-accept threshold at any confidence.

That is the design working, and it is also the design's biggest open cost. Per-
predicate accept-rate is tracked here for exactly that reason: a rate near 100%
means the gate is theatre, and near 10% means the extractor is wasting a
reviewer's time. Neither is visible without measuring it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from company_brain.schemas.edges import Edge, EdgeStatus
from company_brain.schemas.nodes import Node
from company_brain.store.repository import Repository


class Decision(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class PendingEdge:
    """One proposed edge awaiting a human."""

    node_id: str
    node_title: str
    edge: Edge

    @property
    def key(self) -> str:
        return f"{self.node_id}|{self.edge.predicate}|{self.edge.object}"

    def quote(self) -> str:
        for evidence in self.edge.evidence:
            if evidence.quote:
                return evidence.quote.strip()
        return ""


@dataclass(slots=True)
class QueueStats:
    by_predicate: dict[str, int] = field(default_factory=dict)
    total: int = 0
    with_evidence: int = 0

    def add(self, item: PendingEdge) -> None:
        key = str(item.edge.predicate)
        self.by_predicate[key] = self.by_predicate.get(key, 0) + 1
        self.total += 1
        if item.edge.evidence:
            self.with_evidence += 1


class ReviewQueue:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def pending_edges(self, predicate: str | None = None) -> list[PendingEdge]:
        """Every proposed edge in the store, sorted for stable paging."""
        out: list[PendingEdge] = []
        for node in self.repo.walk():
            for edge in node.frontmatter.relations:
                if edge.status is not EdgeStatus.PROPOSED:
                    continue
                if predicate and str(edge.predicate) != predicate:
                    continue
                out.append(PendingEdge(node.id, node.frontmatter.title, edge))
        out.sort(key=lambda p: (str(p.edge.predicate), p.node_id, p.edge.object))
        return out

    def stats(self) -> QueueStats:
        stats = QueueStats()
        for item in self.pending_edges():
            stats.add(item)
        return stats

    def decide(self, key: str, decision: Decision) -> Node:
        """Accept or reject one proposed edge.

        A rejection is recorded as `status: rejected`, not deleted. Rejected
        proposals are the only signal available for tuning the §11 thresholds —
        throwing them away means never learning that a gate is miscalibrated.
        """
        node_id, predicate, obj = key.split("|", 2)
        node = self.repo.get(node_id)

        target = EdgeStatus.ACCEPTED if decision is Decision.ACCEPTED else EdgeStatus.REJECTED
        updated: list[Edge] = []
        found = False
        for edge in node.frontmatter.relations:
            if str(edge.predicate) == predicate and edge.object == obj:
                if edge.status is not EdgeStatus.PROPOSED:
                    raise ValueError(f"{key} is {edge.status}, not pending")
                updated.append(edge.model_copy(update={"status": target}))
                found = True
            else:
                updated.append(edge)
        if not found:
            raise KeyError(key)

        revised = Node(
            frontmatter=node.frontmatter.model_copy(update={"relations": tuple(updated)}),
            body=node.body,
        )
        self.repo.put(revised)
        return revised

    def accept_rate(self) -> dict[str, tuple[int, int]]:
        """Per-predicate (accepted, decided) counts.

        The number that says whether the gates are calibrated. Reported by
        `cb review stats`; it is the metric ARCHITECTURE §11 asks for and the
        one that decides whether the review burden is sustainable.
        """
        tally: dict[str, list[int]] = {}
        for node in self.repo.walk():
            for edge in node.frontmatter.relations:
                if edge.status not in (EdgeStatus.ACCEPTED, EdgeStatus.REJECTED):
                    continue
                if str(edge.provenance) != "llm":
                    continue  # structural edges bypass the gate; don't flatter the stat
                bucket = tally.setdefault(str(edge.predicate), [0, 0])
                bucket[1] += 1
                if edge.status is EdgeStatus.ACCEPTED:
                    bucket[0] += 1
        return {k: (v[0], v[1]) for k, v in sorted(tally.items())}
