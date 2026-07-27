"""Fixtures for the dual-backend index conformance suite.

`MemoryIndex` and `PostgresIndex` implement one protocol two completely different
ways — a Python predicate over a dict, and a SQL join over a VALUES list. The
only thing keeping them honest is running the same tests against both, which is
what the `index` fixture here is for.

Postgres is opt-in through `CB_TEST_DSN`. Without it the memory parameter still
runs and the postgres parameter skips, so the suite is useful on a laptop with no
Docker and complete in CI with one:

    supabase start
    CB_TEST_DSN="postgresql://postgres:postgres@127.0.0.1:54322/postgres" \
      COMPANY_BRAIN_OFFLINE=1 uv run pytest tests/integration -q
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from company_brain.index.base import HashingEmbedder, Index

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = REPO_ROOT / "supabase" / "migrations"

DSN_ENV = "CB_TEST_DSN"
SKIP_REASON = (
    f"{DSN_ENV} is unset — start Postgres (`supabase start`) and export it to run the "
    "SQL half of the conformance suite"
)


def dsn_or_none() -> str | None:
    return os.environ.get(DSN_ENV) or None


@pytest.fixture(scope="session")
def postgres_dsn() -> str:
    dsn = dsn_or_none()
    if dsn is None:
        pytest.skip(SKIP_REASON)
    return dsn


@pytest.fixture(scope="session")
def migrated_dsn(postgres_dsn: str) -> str:
    """Apply `supabase/migrations/*.sql` once per session.

    The migrations are written idempotently (`create ... if not exists`, and a
    guarded `create type`), so re-running them against a warm database is a
    no-op rather than an error. That is a property worth relying on here and
    worth keeping true.
    """
    import psycopg

    files = sorted(MIGRATIONS.glob("*.sql"))
    if not files:
        pytest.skip(f"no migrations found under {MIGRATIONS}")

    with psycopg.connect(postgres_dsn, autocommit=True) as conn:
        for path in files:
            conn.execute(path.read_text())
    return postgres_dsn


@pytest.fixture(params=["memory", "postgres"])
def index(request: pytest.FixtureRequest) -> Iterator[Index]:
    """The same protocol, both ways round.

    Both backends share `HashingEmbedder`: it needs no API key, it is exactly
    reproducible, and a vector comparison across two indexes only means anything
    if both sides embedded the text identically.
    """
    if request.param == "memory":
        from company_brain.index.memory import MemoryIndex

        yield MemoryIndex(HashingEmbedder())
        return

    if dsn_or_none() is None:
        pytest.skip(SKIP_REASON)

    from company_brain.index.postgres import PostgresIndex

    dsn: str = request.getfixturevalue("migrated_dsn")
    backend = PostgresIndex(dsn, HashingEmbedder())
    try:
        yield backend
    finally:
        backend.close()


@pytest.fixture
def backend_name(request: pytest.FixtureRequest) -> Any:
    """Which backend the current `index` parameter is, for divergence tests."""
    return request.node.callspec.params.get("index")
