"""PostgresIndex against a real database.

Runs the shared conformance suite — the same assertions `MemoryIndex` answers in
tests/unit/test_index_conformance.py — plus the things that only mean anything
against SQL: that the ACL predicate is evaluated by the database rather than in
Python, and that a failed rebuild does not leave a half-built index.

Needs a Postgres with pgvector:

    supabase start
    uv run pytest -m postgres

Point `CB_TEST_DATABASE_URL` elsewhere to use a different one. Without a
reachable database every test here SKIPS — it does not pass. A green run that
never touched Postgres would be worse than no test at all.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from company_brain.index.base import HashingEmbedder
from company_brain.schemas.acl import Sensitivity
from tests.index_conformance import (
    COMP,
    MIXED_HIGH,
    MIXED_LOW,
    OPEN_REF,
    IndexConformance,
    corpus,
    node_ids,
)

pytestmark = [pytest.mark.integration, pytest.mark.postgres]

psycopg = pytest.importorskip("psycopg", reason="psycopg is not installed")

from company_brain.index.postgres import (  # noqa: E402  (after importorskip)
    PostgresIndex,
    PushdownError,
)

# Supabase's local stack, per supabase/config.toml.
DEFAULT_DSN = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
DSN = os.environ.get("CB_TEST_DATABASE_URL", DEFAULT_DSN)
MIGRATIONS = Path(__file__).resolve().parents[2] / "supabase" / "migrations"


def _connect() -> Any:
    return psycopg.connect(DSN, connect_timeout=3, autocommit=False)


@pytest.fixture(scope="session")
def database() -> Iterator[Any]:
    """A connection with the migrations applied, or a skip explaining why not."""
    try:
        conn = _connect()
    except psycopg.OperationalError as exc:  # pragma: no cover - environment dependent
        pytest.skip(
            f"no Postgres at {DSN} ({str(exc).strip().splitlines()[0]}). "
            "Run `supabase start`, or set CB_TEST_DATABASE_URL."
        )

    with conn:
        try:
            with conn.cursor() as cur:
                cur.execute("select 1 from pg_available_extensions where name = 'vector'")
                if cur.fetchone() is None:  # pragma: no cover - environment dependent
                    pytest.skip(f"pgvector is not available on {DSN}")
            # The migrations are idempotent (IF NOT EXISTS throughout), so this
            # works against a fresh database and a `supabase db reset` alike.
            for path in sorted(MIGRATIONS.glob("*.sql")):
                with conn.cursor() as cur:
                    cur.execute(path.read_text())
            conn.commit()
            yield conn
        finally:
            conn.rollback()


@pytest.fixture
def pg_index(database: Any) -> Iterator[PostgresIndex]:
    """Function-scoped: every test rebuilds, and rebuild truncates, so tests are
    isolated without a per-test schema."""
    instance = PostgresIndex(DSN, HashingEmbedder(), connection=database)
    yield instance
    database.rollback()


# The postgres-only tests below take `pg_index` directly; the conformance
# subclass has to rebind it, because a fixture on the base class shadows a
# module-level one of the same name.
index = pg_index


class TestPostgresIndexConformance(IndexConformance):
    """The shared contract. Every assertion here also runs against MemoryIndex."""

    @pytest.fixture
    def index(self, pg_index: PostgresIndex) -> PostgresIndex:
        return pg_index


class TrapVisibility:
    """Exposes real grants, but screams if anyone evaluates it row by row.

    This is the executable form of "filtering must happen in the query". The
    elevation probe is a single fixed ref and is allowed through; any other call
    means rows were fetched and then filtered in Python.
    """

    def __init__(self, refs: dict[str, Sensitivity]) -> None:
        self._ceilings = refs
        self.refs = frozenset(refs)
        self.calls: list[tuple[str, Sensitivity]] = []

    def allows(self, acl_ref: str, sensitivity: Sensitivity) -> bool:
        if acl_ref.startswith("cb_probe_elevated:"):
            return False
        self.calls.append((acl_ref, sensitivity))
        raise AssertionError(
            f"the ACL predicate was evaluated in Python for {acl_ref!r}; "
            "it must be a join in the query"
        )

    def ceiling(self, acl_ref: str) -> Sensitivity | None:
        return self._ceilings.get(acl_ref)


class AllowsOnlyVisibility:
    """A conforming `Visibility` with nothing else — cannot be pushed down."""

    def allows(self, acl_ref: str, sensitivity: Sensitivity) -> bool:
        return True


class TestFilteringHappensInSql:
    def test_lexical_search_never_calls_allows_per_row(self, index: PostgresIndex) -> None:
        index.rebuild(corpus())
        trap = TrapVisibility({OPEN_REF: Sensitivity.INTERNAL})

        hits = index.search_lexical("vendor renewal", trap, 10)

        assert trap.calls == []
        assert node_ids(hits), "the query returned nothing; the trap proved nothing"
        assert COMP not in node_ids(hits)

    def test_vector_search_never_calls_allows_per_row(self, index: PostgresIndex) -> None:
        index.rebuild(corpus())
        trap = TrapVisibility({OPEN_REF: Sensitivity.INTERNAL})

        hits = index.search_vector("vendor renewal", trap, 10)

        assert trap.calls == []
        assert COMP not in node_ids(hits)

    def test_the_ceiling_comparison_is_the_database_enum_ordering(
        self, index: PostgresIndex
    ) -> None:
        """`sensitivity <= ceiling` in SQL must mean what `at_least` means in
        Python: a restricted ceiling admits internal rows beneath it."""
        index.rebuild(corpus())
        trap = TrapVisibility({"gdrive:folder:MIXED": Sensitivity.RESTRICTED})

        found = node_ids(index.search_lexical("purchasing", trap, 10))

        assert {MIXED_LOW, MIXED_HIGH} <= found
        assert trap.calls == []

    def test_a_visibility_that_cannot_be_pushed_down_is_refused(
        self, index: PostgresIndex
    ) -> None:
        """Fail closed and loudly. Silently filtering in Python instead would
        return plausible rows and reintroduce the LIMIT truncation."""
        index.rebuild(corpus())
        with pytest.raises(PushdownError, match="grant pairs"):
            index.search_lexical("vendor renewal", AllowsOnlyVisibility(), 10)


class TestRebuildIsAtomic:
    def test_a_failed_rebuild_leaves_the_previous_index_intact(
        self, index: PostgresIndex
    ) -> None:
        """The index is a cache, but a *half* cache is worse than a stale one:
        `cb doctor` would report drift that no re-run can explain."""
        index.rebuild(corpus())
        before = index.stats()

        def exploding() -> Any:
            yield from corpus()[:2]
            raise RuntimeError("connector died mid-rebuild")

        with pytest.raises(RuntimeError):
            index.rebuild(exploding())

        assert index.stats() == before

    def test_embedder_dimensions_are_checked_against_the_schema(self) -> None:
        class WrongDims:
            name = "too-small"
            dims = 8

            def embed(self, texts: Any) -> list[list[float]]:  # pragma: no cover
                return [[0.0] * 8 for _ in texts]

        with pytest.raises(ValueError, match="1536"):
            PostgresIndex(DSN, WrongDims())  # type: ignore[arg-type]
