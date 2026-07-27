"""In-memory index.

A full implementation of the Index protocol, not a stub: real BM25, real cosine,
real ACL filtering, real graph adjacency. It is what makes invariant 2 —
"the index is disposable and rebuildable from markdown" — literally true, and it
lets the whole system run and be tested with no database.

`PostgresIndex` implements the same protocol against Supabase for scale; the
conformance suite runs over both.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable

from company_brain.index.base import (
    Chunk,
    Embedder,
    HashingEmbedder,
    Hit,
    IndexedNode,
    Visibility,
    chunk_node,
    cosine,
    tokenize,
)
from company_brain.schemas.edges import EdgeStatus
from company_brain.schemas.nodes import NodeStatus

_K1 = 1.5
_B = 0.75


class MemoryIndex:
    def __init__(self, embedder: Embedder | None = None) -> None:
        self.embedder = embedder or HashingEmbedder()
        self._nodes: dict[str, IndexedNode] = {}
        self._chunks: dict[str, Chunk] = {}
        self._vectors: dict[str, list[float]] = {}
        self._postings: dict[str, dict[str, int]] = defaultdict(dict)
        self._lengths: dict[str, int] = {}
        self._avg_len = 0.0
        # Only accepted edges are traversable (invariant 10).
        self._out: dict[str, list[tuple[str, str]]] = defaultdict(list)
        self._in: dict[str, list[tuple[str, str]]] = defaultdict(list)

    def rebuild(self, nodes: Iterable[tuple[IndexedNode, str]]) -> int:
        self._nodes.clear()
        self._chunks.clear()
        self._vectors.clear()
        self._postings.clear()
        self._lengths.clear()
        self._out.clear()
        self._in.clear()

        pending: list[Chunk] = []
        for node, body in nodes:
            self._nodes[node.id] = node

            # A tombstone stays *resolvable* — get_node returns it, so an
            # answer issued before the delete resolves to "deleted on <date>"
            # rather than a dangling id (§9.3). It is never *retrievable*: no
            # chunks, so it cannot be a search hit, and `neighbours` will not
            # expand into it.
            #
            # Until this existed, `retain_content=False` was the only thing
            # keeping deleted text out of answers — an accidental safety
            # mechanism that would have failed the moment retention was opted
            # into.
            if node.status != str(NodeStatus.ACTIVE):
                continue

            for edge in node.edges:
                if edge.status is not EdgeStatus.ACCEPTED:
                    continue
                # Adjacency uses the *resolved* subject, so a document
                # reporting "Owen owns capacity planning" produces the edge
                # people/owen-fitz -> processes/capacity-planning, not one
                # rooted at the document.
                subject = edge.resolve_subject(node.id)
                self._out[subject].append((str(edge.predicate), edge.object))
                self._in[edge.object].append((str(edge.predicate), subject))
            pending.extend(
                chunk_node(node.id, node.title, body, node.acl_ref, node.sensitivity)
            )

        vectors = self.embedder.embed([c.text for c in pending]) if pending else []
        for chunk, vector in zip(pending, vectors, strict=True):
            self._chunks[chunk.id] = chunk
            self._vectors[chunk.id] = vector
            tokens = tokenize(f"{chunk.heading_path}\n{chunk.text}")
            self._lengths[chunk.id] = len(tokens)
            for token in tokens:
                self._postings[token][chunk.id] = self._postings[token].get(chunk.id, 0) + 1

        self._avg_len = (
            sum(self._lengths.values()) / len(self._lengths) if self._lengths else 0.0
        )
        return len(self._chunks)

    def get_node(self, node_id: str) -> IndexedNode | None:
        return self._nodes.get(node_id)

    def search_vector(self, query: str, visibility: Visibility, limit: int) -> list[Hit]:
        if not self._vectors:
            return []
        query_vector = self.embedder.embed([query])[0]
        scored = [
            Hit(chunk, cosine(query_vector, self._vectors[cid]), "vector")
            for cid, chunk in self._chunks.items()
            # ACL is applied *before* ranking, not after — post-filtering an ANN
            # result set is what produces the permission-driven recall cliff
            # described in ARCHITECTURE §6.4.
            if visibility.allows(chunk.acl_ref, chunk.sensitivity)
        ]
        scored.sort(key=lambda h: (-h.score, h.chunk.id))
        return [h for h in scored[:limit] if h.score > 0]

    def search_lexical(self, query: str, visibility: Visibility, limit: int) -> list[Hit]:
        terms = tokenize(query)
        if not terms or not self._chunks:
            return []
        total = len(self._chunks)
        scores: dict[str, float] = defaultdict(float)

        for term in set(terms):
            postings = self._postings.get(term)
            if not postings:
                continue
            idf = math.log(1 + (total - len(postings) + 0.5) / (len(postings) + 0.5))
            for chunk_id, freq in postings.items():
                chunk = self._chunks[chunk_id]
                if not visibility.allows(chunk.acl_ref, chunk.sensitivity):
                    continue
                length = self._lengths[chunk_id]
                denominator = freq + _K1 * (
                    1 - _B + _B * (length / self._avg_len if self._avg_len else 1.0)
                )
                scores[chunk_id] += idf * (freq * (_K1 + 1)) / denominator

        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        return [Hit(self._chunks[cid], score, "lexical") for cid, score in ranked[:limit]]

    def neighbours(
        self, node_id: str, predicates: frozenset[str] | None, limit: int
    ) -> list[str]:
        out: list[str] = []
        for predicate, other in self._out.get(node_id, []) + self._in.get(node_id, []):
            if predicates and predicate not in predicates:
                continue
            # Inbound edges to a tombstone are preserved in the store, but a
            # graph walk must not surface deleted content.
            target = self._nodes.get(other)
            if target is not None and target.status != str(NodeStatus.ACTIVE):
                continue
            if other not in out:
                out.append(other)
        return sorted(out)[:limit]

    def edges_of(self, node_id: str) -> list[tuple[str, str]]:
        return sorted(self._out.get(node_id, []))

    def edges_into(self, node_id: str) -> list[tuple[str, str]]:
        """Inbound (predicate, subject) pairs.

        The mirror of `edges_of`, and neither is part of the `Index` protocol —
        `neighbours` is, but it merges both directions and drops the predicate,
        which is exactly the information a caller asking "what does the graph
        say about this node" needs. Entity nodes make the asymmetry matter: a
        Person's own frontmatter carries no relations at all, so everything
        known about them arrives here, as edges other nodes point at them.
        """
        return sorted(self._in.get(node_id, []))

    def stats(self) -> dict[str, int]:
        return {
            "nodes": len(self._nodes),
            "chunks": len(self._chunks),
            "terms": len(self._postings),
            "edges": sum(len(v) for v in self._out.values()),
        }
