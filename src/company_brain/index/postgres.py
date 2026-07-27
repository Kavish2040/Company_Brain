"""Postgres + pgvector implementation of the `Index` protocol.

Conforms to `index.base.Index` unchanged. `MemoryIndex` remains the reference
implementation and the test double; this is the same contract backed by SQL, and
a shared conformance suite drives both so they cannot silently diverge.

**ACL filtering happens in the query.** Every search joins against a VALUES list
of the caller's (acl_ref, ceiling) pairs and compares `sensitivity <= ceiling`
using the ordered `cb_sensitivity` enum. Nothing is fetched and then discarded in
Python: a post-filter would both leak through `LIMIT` (restricted rows consume
slots, silently truncating what a principal is allowed to see) and put the
decision back in application code, which is what invariant 5a exists to prevent.

**On enumerating a `Visibility`.** The protocol in `index/base.py` offers exactly
one method, `allows(acl_ref, sensitivity) -> bool`. A Python predicate cannot be
pushed into SQL — it can be asked about a row, but it cannot be enumerated into a
WHERE clause. Rather than change the protocol (MemoryIndex conforms to it, and it
is the right shape for an in-process index), this module narrows it: it requires
the *public* surface `AccessFilter` already exposes — `refs` and `ceiling(ref)` —
and says so in `PushdownError` when handed something that lacks it. No file
outside this module changes, and the narrowing is checked at the boundary rather
than assumed.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from typing import Any, Protocol, runtime_checkable

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from company_brain.index.base import (
    EMBEDDING_DIMS,
    Chunk,
    Embedder,
    HashingEmbedder,
    Hit,
    IndexedNode,
    Visibility,
    chunk_node,
    tokenize,
)
from company_brain.schemas.acl import Sensitivity
from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance

# A ref no grant table can contain: acl refs are `<connector>:<kind>:<id>` and a
# connector never has this name. Used to ask a Visibility whether it is the
# elevated filter, without depending on the concrete class.
_ELEVATION_PROBE = "cb_probe_elevated:none:none"

_BATCH = 256


class PushdownError(TypeError):
    """A Visibility that cannot be turned into a SQL predicate.

    Raised instead of falling back to filtering in Python. The fallback would
    still return correct-looking rows, which is precisely why it must not exist:
    a leak here is silent, and `LIMIT` would quietly truncate legitimate results.
    """


@runtime_checkable
class EnumerableVisibility(Protocol):
    """`Visibility`, plus the ability to state which grants it is made of.

    `acl.grants.AccessFilter` satisfies this today through its public API. Any
    future filter must too, or it cannot be used against a real database.
    """

    refs: frozenset[str]

    def allows(self, acl_ref: str, sensitivity: Sensitivity) -> bool: ...

    def ceiling(self, acl_ref: str) -> Sensitivity | None: ...


def _is_elevated(visibility: Visibility) -> bool:
    """Does this filter admit everything? Asked, never inspected."""
    return visibility.allows(_ELEVATION_PROBE, Sensitivity.RESTRICTED)


def _grant_pairs(visibility: Visibility) -> list[tuple[str, str]]:
    """The (ref, ceiling) pairs behind a filter, for the SQL join."""
    if not isinstance(visibility, EnumerableVisibility):
        raise PushdownError(
            f"{type(visibility).__name__} exposes only allows(); a SQL index needs the "
            "grant pairs behind it (refs + ceiling). See PushdownError in index/postgres.py."
        )
    pairs: list[tuple[str, str]] = []
    for ref in sorted(visibility.refs):
        ceiling = visibility.ceiling(ref)
        if ceiling is not None:
            pairs.append((ref, str(ceiling)))
    return pairs


def _vector_literal(values: Sequence[float]) -> str:
    """pgvector's text input format. Avoids a dependency on the `pgvector` package."""
    return "[" + ",".join(f"{v:.7g}" for v in values) + "]"


def _tsquery(query: str) -> str | None:
    """OR-of-terms, matching how `MemoryIndex` scores a multi-word query.

    `plainto_tsquery` would AND the terms and answer a narrower question than the
    in-memory index does, so the two would disagree on recall for every query
    longer than one word.
    """
    terms = [t.replace("'", "") for t in tokenize(query)]
    terms = [t for t in terms if t]
    if not terms:
        return None
    return " | ".join(f"'{t}'" for t in terms)


class PostgresIndex:
    """The `Index` protocol over Postgres + pgvector.

    Holds one connection. The index is disposable by construction — `rebuild`
    truncates and repopulates inside a single transaction, so a failed rebuild
    leaves the previous index intact rather than a half-written one.
    """

    def __init__(
        self,
        dsn: str,
        embedder: Embedder | None = None,
        *,
        connection: psycopg.Connection[Any] | None = None,
    ) -> None:
        self.embedder = embedder or HashingEmbedder()
        if self.embedder.dims != EMBEDDING_DIMS:
            raise ValueError(
                f"embedder {self.embedder.name!r} produces {self.embedder.dims} dims; "
                f"the schema pins vector({EMBEDDING_DIMS}). Changing that is a migration "
                "plus a full re-embed."
            )
        self.dsn = dsn
        self._own_connection = connection is None
        self._conn = connection or psycopg.connect(dsn, autocommit=False)

    # ---- lifecycle -------------------------------------------------------

    def close(self) -> None:
        if self._own_connection and not self._conn.closed:
            self._conn.close()

    def __enter__(self) -> PostgresIndex:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ---- write path ------------------------------------------------------

    def rebuild(self, nodes: Iterable[tuple[IndexedNode, str]]) -> int:
        """Drop everything derived and rebuild it from markdown. Invariant 2."""
        node_rows: list[tuple[Any, ...]] = []
        edge_rows: list[tuple[Any, ...]] = []
        chunks: list[Chunk] = []

        for node, body in nodes:
            node_rows.append(
                (
                    node.id,
                    node.type,
                    node.title,
                    node.acl_ref,
                    str(node.sensitivity),
                    node.status,
                    node.content_sha256,
                )
            )
            seen: set[tuple[str, str, str]] = set()
            for edge in node.edges:
                subject = edge.resolve_subject(node.id)
                key = (str(edge.predicate), subject, edge.object)
                if key in seen:
                    # The primary key collapses duplicates; do it here so the
                    # row count matches what the caller handed us.
                    continue
                seen.add(key)
                edge_rows.append(
                    (
                        node.id,
                        str(edge.predicate),
                        subject,
                        edge.object,
                        edge.subject,
                        edge.confidence,
                        str(edge.provenance),
                        str(edge.status),
                        json.dumps([e.model_dump(mode="json") for e in edge.evidence]),
                    )
                )
            chunks.extend(chunk_node(node.id, node.title, body, node.acl_ref, node.sensitivity))

        vectors = self._embed([c.text for c in chunks])

        with self._conn.transaction(), self._conn.cursor() as cur:
            # RESTART IDENTITY is pointless here (no sequences) but CASCADE is
            # not: chunks and embeddings hang off nodes.
            cur.execute("truncate nodes, chunks, embeddings, edges, terms cascade")

            if node_rows:
                cur.executemany(
                    "insert into nodes (id, type, title, acl_ref, sensitivity, status,"
                    " content_sha256) values (%s, %s, %s, %s, %s::cb_sensitivity, %s, %s)",
                    node_rows,
                )
            if edge_rows:
                cur.executemany(
                    "insert into edges (container_id, predicate, subject, object,"
                    " raw_subject, confidence, provenance, status, evidence)"
                    " values (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)",
                    edge_rows,
                )
            if chunks:
                cur.executemany(
                    "insert into chunks (id, node_id, ordinal, heading_path, text,"
                    " token_count, acl_ref, sensitivity)"
                    " values (%s, %s, %s, %s, %s, %s, %s, %s::cb_sensitivity)",
                    [
                        (
                            c.id,
                            c.node_id,
                            c.ordinal,
                            c.heading_path,
                            c.text,
                            len(tokenize(c.text)),
                            c.acl_ref,
                            str(c.sensitivity),
                        )
                        for c in chunks
                    ],
                )
                cur.executemany(
                    "insert into embeddings (chunk_id, model, vec) values (%s, %s, %s::vector)",
                    [
                        (c.id, self.embedder.name, _vector_literal(v))
                        for c, v in zip(chunks, vectors, strict=True)
                    ],
                )
                cur.execute(
                    "insert into terms (term, chunk_count)"
                    " select word, ndoc from ts_stat('select tsv from chunks')"
                    " on conflict (term) do update set chunk_count = excluded.chunk_count"
                )

        return len(chunks)

    def _embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        out: list[list[float]] = []
        for start in range(0, len(texts), _BATCH):
            out.extend(self.embedder.embed(texts[start : start + _BATCH]))
        return out

    # ---- read path -------------------------------------------------------

    def get_node(self, node_id: str) -> IndexedNode | None:
        with self._conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "select id, type, title, acl_ref, sensitivity, status, content_sha256"
                " from nodes where id = %s",
                (node_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            cur.execute(
                "select predicate, raw_subject, object, confidence, provenance, status,"
                " evidence from edges where container_id = %s"
                " order by predicate, coalesce(raw_subject, ''), object",
                (node_id,),
            )
            edges = tuple(_edge_from_row(e) for e in cur.fetchall())

        return IndexedNode(
            id=row["id"],
            type=row["type"],
            title=row["title"],
            acl_ref=row["acl_ref"],
            sensitivity=Sensitivity(row["sensitivity"]),
            status=row["status"],
            content_sha256=row["content_sha256"],
            edges=edges,
        )

    def search_vector(self, query: str, visibility: Visibility, limit: int) -> list[Hit]:
        clause, params = self._acl_clause(visibility, alias="c")
        if clause is None:
            return []

        vector = _vector_literal(self.embedder.embed([query])[0])
        statement = sql.SQL(
            "select {cols}, 1 - (e.vec <=> %s::vector) as score"
            " from chunks c join embeddings e on e.chunk_id = c.id"
            " {acl}"
            # ACL first, ranking second: ordering before filtering lets
            # restricted rows eat the LIMIT (ARCHITECTURE §6.4).
            " where 1 - (e.vec <=> %s::vector) > 0"
            " order by e.vec <=> %s::vector, c.id"
            " limit %s"
        ).format(cols=_CHUNK_COLUMNS, acl=clause)

        with self._conn.cursor(row_factory=dict_row) as cur:
            cur.execute(statement, (vector, *params, vector, vector, limit))
            return [
                Hit(_chunk_from_row(r), float(r["score"]), "vector") for r in cur.fetchall()
            ]

    def search_lexical(self, query: str, visibility: Visibility, limit: int) -> list[Hit]:
        terms = _tsquery(query)
        if terms is None:
            return []
        clause, params = self._acl_clause(visibility, alias="c")
        if clause is None:
            return []

        statement = sql.SQL(
            "select {cols}, ts_rank_cd(c.tsv, q.query) as score"
            " from chunks c cross join to_tsquery('english', %s) as q(query)"
            " {acl}"
            " where c.tsv @@ q.query"
            " order by score desc, c.id"
            " limit %s"
        ).format(cols=_CHUNK_COLUMNS, acl=clause)

        with self._conn.cursor(row_factory=dict_row) as cur:
            cur.execute(statement, (terms, *params, limit))
            return [
                Hit(_chunk_from_row(r), float(r["score"]), "lexical") for r in cur.fetchall()
            ]

    def neighbours(
        self, node_id: str, predicates: frozenset[str] | None, limit: int
    ) -> list[str]:
        """Accepted edges only, both directions, deterministic order."""
        filter_sql = sql.SQL("") if predicates is None else sql.SQL(" and predicate = any(%s)")
        extra: tuple[Any, ...] = () if predicates is None else (sorted(predicates),)

        statement = sql.SQL(
            "select distinct other from ("
            "  select object as other from edges"
            "   where subject = %s and status = 'accepted'{f}"
            "  union"
            "  select subject as other from edges"
            "   where object = %s and status = 'accepted'{f}"
            ") n order by other limit %s"
        ).format(f=filter_sql)

        with self._conn.cursor() as cur:
            cur.execute(statement, (node_id, *extra, node_id, *extra, limit))
            return [r[0] for r in cur.fetchall()]

    def edges_of(self, node_id: str) -> list[tuple[str, str]]:
        """Outbound accepted edges, mirroring `MemoryIndex.edges_of`.

        Not part of the `Index` protocol; `retrieve.hybrid._edge_weight` reads it
        off MemoryIndex specifically. See the note at the end of this module.
        """
        with self._conn.cursor() as cur:
            cur.execute(
                "select predicate, object from edges"
                " where subject = %s and status = 'accepted' order by predicate, object",
                (node_id,),
            )
            return [(r[0], r[1]) for r in cur.fetchall()]

    def stats(self) -> dict[str, int]:
        with self._conn.cursor() as cur:
            cur.execute(
                "select (select count(*) from nodes),"
                " (select count(*) from chunks),"
                " (select count(*) from terms),"
                " (select count(*) from edges where status = 'accepted')"
            )
            nodes, chunks, terms, edges = cur.fetchone() or (0, 0, 0, 0)
        return {"nodes": nodes, "chunks": chunks, "terms": terms, "edges": edges}

    # ---- the ACL predicate ----------------------------------------------

    def _acl_clause(
        self, visibility: Visibility, *, alias: str
    ) -> tuple[sql.Composable | None, tuple[Any, ...]]:
        """The join that enforces (ref, ceiling) pairs inside the query.

        Returns `(None, ())` when the caller can see nothing at all — an empty
        VALUES list is a syntax error, and "no grants" must mean "no rows", never
        "no filter".
        """
        if _is_elevated(visibility):
            return sql.SQL(""), ()

        pairs = _grant_pairs(visibility)
        if not pairs:
            return None, ()

        values = sql.SQL(", ").join(sql.SQL("(%s, %s::cb_sensitivity)") for _ in pairs)
        clause = sql.SQL(
            " join (values {v}) as g (acl_ref, ceiling)"
            "   on {a}.acl_ref = g.acl_ref and {a}.sensitivity <= g.ceiling"
        ).format(v=values, a=sql.Identifier(alias))
        return clause, tuple(x for pair in pairs for x in pair)


_CHUNK_COLUMNS = sql.SQL(
    "c.id, c.node_id, c.ordinal, c.heading_path, c.text, c.acl_ref, c.sensitivity"
)


def _chunk_from_row(row: dict[str, Any]) -> Chunk:
    return Chunk(
        id=row["id"],
        node_id=row["node_id"],
        ordinal=row["ordinal"],
        heading_path=row["heading_path"],
        text=row["text"],
        acl_ref=row["acl_ref"],
        sensitivity=Sensitivity(row["sensitivity"]),
    )


def _edge_from_row(row: dict[str, Any]) -> Edge:
    return Edge(
        predicate=Predicate(row["predicate"]),
        subject=row["raw_subject"],
        object=row["object"],
        confidence=row["confidence"],
        provenance=Provenance(row["provenance"]),
        status=EdgeStatus(row["status"]),
        evidence=tuple(Evidence.model_validate(e) for e in row["evidence"]),
    )


# Left for the merge, deliberately:
#
# 1. `choose_providers()` in app.py still returns MemoryIndex unconditionally.
#    Wiring this in is a constructor swap plus a DSN in config.
# 2. `retrieve.hybrid._edge_weight` narrows on `isinstance(index, MemoryIndex)`
#    and falls back to a flat 0.25 for anything else, so graph expansion would
#    lose its per-predicate weights against Postgres. `edges_of` above has the
#    same signature, so the fix is to duck-type that check rather than name a
#    class. Both files are owned by another session right now.
