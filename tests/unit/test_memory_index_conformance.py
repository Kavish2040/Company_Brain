"""MemoryIndex against the shared index conformance suite.

The Postgres half of this lives in tests/integration/test_postgres_index.py and
runs the same assertions. Anything added there is added here for free, which is
the point: the two backends cannot drift without one of them going red.
"""

from __future__ import annotations

from typing import Any

import pytest

from company_brain.index.base import HashingEmbedder
from company_brain.index.memory import MemoryIndex
from tests.index_conformance import IndexConformance


class TestMemoryIndexConformance(IndexConformance):
    @pytest.fixture
    def index(self) -> Any:
        return MemoryIndex(HashingEmbedder())
