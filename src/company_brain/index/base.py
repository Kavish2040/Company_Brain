"""The derived index: chunking, embedding, and the Index protocol.

Postgres is a cache with a query planner (invariant 1). Everything here is
rebuildable from the markdown store, which is why an in-memory implementation is
a legitimate backend and not a mock — `MemoryIndex` *is* the rebuild.

Chunks inherit their node's `acl_ref` so the permission filter is one indexed
predicate in the same query as the vector search, rather than a post-filter.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from company_brain.schemas.acl import Sensitivity
from company_brain.schemas.edges import Edge
from company_brain.store.fences import strip_regions

EMBEDDING_DIMS = 1536  # pgvector HNSW caps at 2000 for `vector`; see CLAUDE.md
_TOKEN = re.compile(r"[a-z0-9][a-z0-9'_-]*")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class Chunk:
    id: str
    node_id: str
    ordinal: int
    heading_path: str
    text: str
    acl_ref: str
    sensitivity: Sensitivity


@dataclass(frozen=True, slots=True)
class IndexedNode:
    id: str
    type: str
    title: str
    acl_ref: str
    sensitivity: Sensitivity
    status: str
    content_sha256: str
    edges: tuple[Edge, ...]


@dataclass(frozen=True, slots=True)
class Hit:
    chunk: Chunk
    score: float
    source: str  # "vector" | "lexical" | "graph"


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


@runtime_checkable
class Embedder(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def dims(self) -> int: ...

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class HashingEmbedder:
    """Deterministic hashed bag-of-words with sublinear term weighting.

    Not a semantic model — it will not match "renewal" to "contract extension".
    But it is a *real* vector space with real cosine similarity, it needs no API
    key, and it is exactly reproducible, so it can back CI and the offline demo.
    Swapping in `OpenAIEmbedder` changes one constructor argument.
    """

    name = "hashing-v1"

    def __init__(self, dims: int = EMBEDDING_DIMS) -> None:
        self.dims = dims

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        vector = [0.0] * self.dims
        counts: dict[str, int] = {}
        for token in tokenize(text):
            counts[token] = counts.get(token, 0) + 1
        for token, count in counts.items():
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dims
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[bucket] += sign * (1.0 + math.log(count))
        norm = math.sqrt(sum(v * v for v in vector))
        return [v / norm for v in vector] if norm else vector


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


def chunk_node(
    node_id: str,
    title: str,
    body: str,
    acl_ref: str,
    sensitivity: Sensitivity,
    *,
    max_tokens: int = 220,
) -> list[Chunk]:
    """Structure-aware chunking: split at headings, then pack to a token bound.

    Generated regions are stripped first — they are derived from edges that are
    already indexed, so chunking them would let a machine-written summary
    outrank the source it was written from.
    """
    text = strip_regions(body)
    sections: list[tuple[str, str]] = []
    matches = list(_HEADING.finditer(text))

    if not matches:
        sections.append((title, text))
    else:
        if matches[0].start() > 0:
            preamble = text[: matches[0].start()].strip()
            if preamble:
                sections.append((title, preamble))
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            heading = match.group(2).strip()
            content = text[match.end() : end].strip()
            if content:
                sections.append((f"{title} > {heading}", content))

    chunks: list[Chunk] = []
    for heading_path, content in sections:
        for piece in _pack(content, max_tokens):
            ordinal = len(chunks)
            chunks.append(
                Chunk(
                    id=f"{node_id}#{ordinal}",
                    node_id=node_id,
                    ordinal=ordinal,
                    heading_path=heading_path,
                    text=piece,
                    acl_ref=acl_ref,
                    sensitivity=sensitivity,
                )
            )
    return chunks


def _pack(content: str, max_tokens: int) -> list[str]:
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    out: list[str] = []
    buffer: list[str] = []
    size = 0
    for paragraph in paragraphs:
        length = len(tokenize(paragraph))
        if buffer and size + length > max_tokens:
            out.append("\n\n".join(buffer))
            buffer, size = [], 0
        buffer.append(paragraph)
        size += length
    if buffer:
        out.append("\n\n".join(buffer))
    return out or [content]


@runtime_checkable
class Visibility(Protocol):
    """The access predicate, as the index sees it.

    Deliberately narrow: one method, no sets to unpack. `acl.AccessFilter`
    satisfies it structurally, so an index implementation cannot re-derive the
    decision — it can only ask. A `PostgresIndex` translates this into a SQL
    predicate over (acl_ref, sensitivity) pairs; it must not translate loose
    ref and tier lists, which is not the same predicate.
    """

    def allows(self, acl_ref: str, sensitivity: Sensitivity) -> bool: ...


@runtime_checkable
class Index(Protocol):
    """Query surface. Every search takes the caller's visibility, and applies it
    before ranking rather than after."""

    def rebuild(self, nodes: Iterable[tuple[IndexedNode, str]]) -> int: ...

    def get_node(self, node_id: str) -> IndexedNode | None: ...

    def search_vector(self, query: str, visibility: Visibility, limit: int) -> list[Hit]: ...

    def search_lexical(self, query: str, visibility: Visibility, limit: int) -> list[Hit]: ...

    def neighbours(
        self, node_id: str, predicates: frozenset[str] | None, limit: int
    ) -> list[str]: ...

    def stats(self) -> dict[str, int]: ...
