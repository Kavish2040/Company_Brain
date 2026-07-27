"""OpenAI embeddings.

`text-embedding-3-large` reduced to 1536 dimensions rather than its native 3072:
pgvector's HNSW index caps at 2000 dimensions for the `vector` type, so 3072
cannot be indexed without switching to `halfvec`. The model supports native
dimension reduction, so 1536 buys the better model under the index limit.

The dimension is pinned in the migration. Changing it later is a migration plus
a full re-embed of the corpus, not a config tweak — which is why `dims` is
asserted against EMBEDDING_DIMS at construction rather than trusted.
"""

from __future__ import annotations

import os
from collections.abc import Sequence

from openai import OpenAI

from company_brain.index.base import EMBEDDING_DIMS

DEFAULT_MODEL = "text-embedding-3-large"
# The API rejects oversized batches; chunk requests rather than discovering the
# limit in production.
MAX_BATCH = 256


class OpenAIEmbedder:
    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        dims: int = EMBEDDING_DIMS,
        client: OpenAI | None = None,
    ) -> None:
        if dims > 2000:
            raise ValueError(
                f"{dims} dimensions exceeds pgvector's HNSW limit of 2000 for the "
                f"`vector` type; use halfvec or reduce dimensions"
            )
        self._model = model
        self._dims = dims
        self.client = client or OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    @property
    def name(self) -> str:
        return f"{self._model}@{self._dims}"

    @property
    def dims(self) -> int:
        return self._dims

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        out: list[list[float]] = []
        for start in range(0, len(texts), MAX_BATCH):
            batch = list(texts[start : start + MAX_BATCH])
            # The API errors on empty strings; substitute a single space and
            # keep positional alignment with the caller's list.
            safe = [t if t.strip() else " " for t in batch]
            response = self.client.embeddings.create(
                model=self._model, input=safe, dimensions=self._dims
            )
            # Responses are returned in request order, but the index field is
            # authoritative — sort by it rather than assuming.
            for item in sorted(response.data, key=lambda d: d.index):
                out.append(list(item.embedding))
        return out
