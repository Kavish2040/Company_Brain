"""Hybrid retrieval: vector + lexical, fused, then expanded along typed edges.

Lexical is not optional here. This corpus is full of exact identifiers — tool
names, people, process names, ticket IDs — and embeddings blur precisely those.
Reciprocal Rank Fusion combines the two without needing the score scales to be
comparable, which they are not.

Every expanded node is re-checked against the principal's visible set. Traversal
is the easiest place to leak: the seed is filtered, and then a graph hop walks
straight into a node nobody checked.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from company_brain.acl.grants import AccessFilter
from company_brain.index.base import Hit, Index
from company_brain.index.memory import MemoryIndex

RRF_K = 60

# Traversal weights. `mentions` is deliberately low: it is the most common edge
# and the least informative, so an unweighted walk drowns the answer in
# everything that happens to name the same tool.
PREDICATE_WEIGHTS: dict[str, float] = {
    "owns": 1.0,
    "authored_by": 0.7,
    "handoff_to": 0.7,
    "depends_on": 0.6,
    "supersedes": 0.5,
    "operated_by": 0.5,
    "mentions": 0.25,
}


@dataclass(slots=True)
class RetrievedNode:
    node_id: str
    title: str
    score: float
    snippets: list[str] = field(default_factory=list)
    via: str = "seed"
    hops: int = 0


@dataclass(slots=True)
class Retrieval:
    query: str
    nodes: list[RetrievedNode]
    seed_count: int
    expanded_count: int
    filtered_out: int


def reciprocal_rank_fusion(*rankings: list[Hit]) -> dict[str, float]:
    fused: dict[str, float] = {}
    for ranking in rankings:
        for rank, hit in enumerate(ranking, start=1):
            fused[hit.chunk.id] = fused.get(hit.chunk.id, 0.0) + 1.0 / (RRF_K + rank)
    return fused


class HybridRetriever:
    def __init__(self, index: Index, access: AccessFilter) -> None:
        self.index = index
        self.access = access

    def retrieve(
        self, query: str, *, limit: int = 8, per_leg: int = 25, max_hops: int = 2
    ) -> Retrieval:
        # The filter goes in whole. Unpacking it into refs and tiers here is what
        # let the index answer a different question than `allows` does.
        vector = self.index.search_vector(query, self.access, per_leg)
        lexical = self.index.search_lexical(query, self.access, per_leg)
        fused = reciprocal_rank_fusion(vector, lexical)

        by_chunk = {h.chunk.id: h for h in [*vector, *lexical]}
        per_node: dict[str, RetrievedNode] = {}
        for chunk_id, score in sorted(fused.items(), key=lambda kv: (-kv[1], kv[0])):
            chunk = by_chunk[chunk_id].chunk
            node = per_node.get(chunk.node_id)
            if node is None:
                indexed = self.index.get_node(chunk.node_id)
                node = RetrievedNode(
                    node_id=chunk.node_id,
                    title=indexed.title if indexed else chunk.node_id,
                    score=0.0,
                )
                per_node[chunk.node_id] = node
            node.score += score
            if len(node.snippets) < 3:
                node.snippets.append(chunk.text.strip())

        seeds = sorted(per_node.values(), key=lambda n: (-n.score, n.node_id))[:limit]
        seed_ids = {n.node_id for n in seeds}
        results = list(seeds)
        filtered_out = 0

        # Expansion scores are derived from the *parent's* score, never from an
        # independent scale. Mixing RRF scores (~0.03) with raw edge weights
        # (~0.25) let every graph hop outrank the seed it came from, burying the
        # documents that actually matched the query.
        parent_score = {n.node_id: n.score for n in seeds}
        frontier = list(seed_ids)
        for hop in range(1, max_hops + 1):
            next_frontier: list[str] = []
            for node_id in frontier:
                base = parent_score.get(node_id, 0.0)
                for neighbour in self.index.neighbours(node_id, None, limit=12):
                    if neighbour in seed_ids or any(r.node_id == neighbour for r in results):
                        continue
                    indexed = self.index.get_node(neighbour)
                    if indexed is None:
                        continue
                    # Re-check every hop. The seed was filtered; the neighbour
                    # was not, and a graph walk is the easiest way to leak.
                    if not self.access.allows(indexed.acl_ref, indexed.sensitivity):
                        filtered_out += 1
                        continue
                    weight = _edge_weight(self.index, node_id, neighbour)
                    score = base * weight * (0.5**hop)
                    parent_score[neighbour] = score
                    results.append(
                        RetrievedNode(
                            node_id=neighbour,
                            title=indexed.title,
                            score=score,
                            via=node_id,
                            hops=hop,
                        )
                    )
                    next_frontier.append(neighbour)
            frontier = next_frontier
            if not frontier:
                break

        results.sort(key=lambda n: (-n.score, n.node_id))
        return Retrieval(
            query=query,
            nodes=results[: limit * 3],
            seed_count=len(seeds),
            expanded_count=len(results) - len(seeds),
            filtered_out=filtered_out,
        )


def _edge_weight(index: Index, source: str, target: str) -> float:
    if not isinstance(index, MemoryIndex):
        return PREDICATE_WEIGHTS.get("mentions", 0.25)
    best = 0.0
    for predicate, other in index.edges_of(source):
        if other == target:
            best = max(best, PREDICATE_WEIGHTS.get(predicate, 0.2))
    return best or 0.2
