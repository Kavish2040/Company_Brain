"""Entity and edge extraction, and the cache that makes it reproducible.

Sampling parameters were removed from the current Claude models — `temperature`,
`top_p` and `top_k` all return a 400 — so there is no knob that makes a model
call reproducible. The content-addressed cache in this module is therefore not
an optimisation; it is the only mechanism by which re-ingestion can produce a
byte-identical tree (ARCHITECTURE §4).

The cache is committed to the repo. `--frozen` (what CI runs) turns a cache miss
into an error rather than a model call, so the acceptance test exercises our
pipeline and not the provider's mood.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance
from company_brain.store.backend import StoreBackend

CACHE_PREFIX = "_cache/extraction"


@dataclass(frozen=True, slots=True)
class ExtractionRequest:
    node_id: str
    title: str
    body: str
    content_sha256: str


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    """Edges the extractor believes in, before the §11 gate is applied."""

    edges: tuple[Edge, ...]
    model: str
    prompt_version: str
    unresolved: tuple[str, ...] = ()


class CacheMiss(RuntimeError):
    """Frozen mode hit an uncached document."""

    def __init__(self, node_id: str, key: str) -> None:
        super().__init__(
            f"no cached extraction for {node_id} (key {key}); "
            f"re-run without --frozen to populate it"
        )
        self.node_id = node_id
        self.key = key


@runtime_checkable
class Extractor(Protocol):
    @property
    def model(self) -> str: ...

    @property
    def prompt_version(self) -> str: ...

    def extract(self, request: ExtractionRequest) -> ExtractionResult: ...


def cache_key(request: ExtractionRequest, model: str, prompt_version: str) -> str:
    """Address an extraction by everything that could change its output.

    Note what is *absent*: no decode parameters, because there are none to
    record on current models.
    """
    material = "\x00".join([request.content_sha256, prompt_version, model])
    return hashlib.blake2b(material.encode("utf-8"), digest_size=16).hexdigest()


class CachedExtractor:
    """Wraps an extractor with the committed on-disk cache."""

    def __init__(
        self, inner: Extractor, backend: StoreBackend, *, frozen: bool = False
    ) -> None:
        self.inner = inner
        self.backend = backend
        self.frozen = frozen
        self.hits = 0
        self.misses = 0

    @property
    def model(self) -> str:
        return self.inner.model

    @property
    def prompt_version(self) -> str:
        return self.inner.prompt_version

    def key_for(self, request: ExtractionRequest) -> str:
        return cache_key(request, self.inner.model, self.inner.prompt_version)

    def extract(self, request: ExtractionRequest) -> ExtractionResult:
        key = self.key_for(request)
        path = f"{CACHE_PREFIX}/{key}.json"

        cached = self.backend.read_text(path)
        if cached is not None:
            self.hits += 1
            return _from_json(json.loads(cached))

        if self.frozen:
            raise CacheMiss(request.node_id, key)

        self.misses += 1
        result = self.inner.extract(request)
        self.backend.write_text(path, _to_json(result))
        return result


def _to_json(result: ExtractionResult) -> str:
    payload = {
        "model": result.model,
        "prompt_version": result.prompt_version,
        "unresolved": sorted(result.unresolved),
        "edges": [
            {
                "predicate": str(e.predicate),
                "object": e.object,
                "confidence": round(e.confidence, 4),
                "provenance": str(e.provenance),
                "status": str(e.status),
                "evidence": [
                    {
                        "node": ev.node,
                        "span": list(ev.span) if ev.span else None,
                        "quote": ev.quote,
                    }
                    for ev in e.evidence
                ],
            }
            for e in sorted(result.edges, key=lambda e: e.sort_key())
        ],
    }
    # sort_keys + fixed separators: the cache is committed, so its own
    # serialization has to be as deterministic as the markdown it feeds.
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _from_json(payload: dict[str, Any]) -> ExtractionResult:
    edges = tuple(
        Edge(
            predicate=Predicate(e["predicate"]),
            object=e["object"],
            confidence=e["confidence"],
            provenance=Provenance(e["provenance"]),
            status=EdgeStatus(e["status"]),
            evidence=tuple(
                Evidence(
                    node=ev["node"],
                    span=(ev["span"][0], ev["span"][1]) if ev.get("span") else None,
                    quote=ev.get("quote"),
                )
                for ev in e.get("evidence", [])
            ),
        )
        for e in payload["edges"]
    )
    return ExtractionResult(
        edges=edges,
        model=payload["model"],
        prompt_version=payload["prompt_version"],
        unresolved=tuple(payload.get("unresolved", ())),
    )
