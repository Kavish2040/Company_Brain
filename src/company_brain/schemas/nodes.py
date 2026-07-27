"""Nodes and their frontmatter.

The frontmatter model is the single source of truth for what a canonical
markdown file contains. Two rules shape it:

* No wall-clock timestamps (invariant 4). Every time in here comes from the
  source artifact. Ingestion time lives in Postgres ``ingest_runs``.
* Every field must serialize deterministically, so collections are tuples and
  the emitter sorts them by a declared key (invariant 3).
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from company_brain.schemas.acl import AclRef
from company_brain.schemas.edges import Edge
from company_brain.schemas.ids import TYPE_PLURALS, split_id


class NodeType(StrEnum):
    DOCUMENT = "Document"
    PERSON = "Person"
    ACCOUNT = "Account"  # bots and shared inboxes; not people (§10.2)
    TEAM = "Team"
    TOOL = "Tool"
    PROCESS = "Process"
    DECISION = "Decision"


class NodeStatus(StrEnum):
    ACTIVE = "active"
    DELETED = "deleted"  # tombstoned after an upstream delete (§9.3)
    MERGED = "merged"  # losing side of a reversible entity merge (§10.1)


class SourceRef(BaseModel):
    """Provenance of a Document node. Absent on synthesized entity nodes."""

    model_config = ConfigDict(frozen=True)

    connector: str
    uri: str
    external_id: str
    external_version: str | None = None
    content_sha256: str

    @field_validator("content_sha256")
    @classmethod
    def _is_sha256(cls, v: str) -> str:
        if len(v) != 64 or not all(c in "0123456789abcdef" for c in v):
            raise ValueError("content_sha256 must be 64 lowercase hex chars")
        return v


class NormalizerRef(BaseModel):
    """Which converter produced the body, and at what version.

    Recorded in the file so a converter upgrade shows up as a reviewable diff
    rather than silent churn across the corpus (docs/ARCHITECTURE.md §4).
    """

    model_config = ConfigDict(frozen=True)

    name: str
    version: str


class ExtractionStatus(StrEnum):
    ACCEPTED = "accepted"
    PARTIAL = "partial"
    PROPOSED = "proposed"
    NONE = "none"


class ExtractionRef(BaseModel):
    """Which model produced the relations block, under which prompt.

    ``cache_key`` addresses the committed extraction cache. Because sampling
    parameters were removed from the current models, there is no temperature to
    pin — the cache is the *only* thing making re-ingestion reproducible
    (docs/ARCHITECTURE.md §4).
    """

    model_config = ConfigDict(frozen=True)

    model: str
    prompt_version: str
    cache_key: str
    status: ExtractionStatus


class Timestamps(BaseModel):
    model_config = ConfigDict(frozen=True)

    created: datetime | None = None
    modified: datetime | None = None

    @model_validator(mode="after")
    def _tz_aware_and_ordered(self) -> Self:
        for name in ("created", "modified"):
            value = getattr(self, name)
            if value is not None and value.tzinfo is None:
                raise ValueError(f"timestamps.{name} must be timezone-aware")
        if self.created and self.modified and self.modified < self.created:
            raise ValueError("timestamps.modified precedes timestamps.created")
        return self


class Frontmatter(BaseModel):
    """The YAML block at the top of every canonical file."""

    model_config = ConfigDict(frozen=True)

    id: str
    type: NodeType
    title: str
    acl: AclRef
    status: NodeStatus = NodeStatus.ACTIVE

    source: SourceRef | None = None
    authors: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    timestamps: Timestamps = Timestamps()
    normalizer: NormalizerRef | None = None
    extraction: ExtractionRef | None = None
    relations: tuple[Edge, ...] = ()

    # Tombstone fields, set only when status is not ACTIVE.
    redirects_to: str | None = None
    deleted_upstream_at: datetime | None = None
    content_retained: bool | None = None

    @field_validator("id")
    @classmethod
    def _id_parses(cls, v: str) -> str:
        split_id(v)
        return v

    @model_validator(mode="after")
    def _id_matches_type(self) -> Self:
        node_type, _ = split_id(self.id)
        if node_type != str(self.type):
            raise ValueError(
                f"id {self.id!r} implies type {node_type}, frontmatter says {self.type}"
            )
        return self

    @model_validator(mode="after")
    def _documents_have_a_source(self) -> Self:
        # A Document with no source is either a bug in a connector or a
        # hand-written file masquerading as an ingested one. Both are worth
        # catching at parse time.
        if self.type is NodeType.DOCUMENT and self.source is None:
            raise ValueError(f"Document node {self.id!r} has no source block")
        return self

    @model_validator(mode="after")
    def _tombstones_are_coherent(self) -> Self:
        if self.status is NodeStatus.MERGED and self.redirects_to is None:
            raise ValueError(f"merged node {self.id!r} must set redirects_to")
        if self.status is NodeStatus.DELETED and self.deleted_upstream_at is None:
            raise ValueError(f"deleted node {self.id!r} must set deleted_upstream_at")
        if self.redirects_to is not None:
            split_id(self.redirects_to)
            if self.redirects_to == self.id:
                raise ValueError(f"node {self.id!r} redirects to itself")
        return self

    @model_validator(mode="after")
    def _no_self_edges(self) -> Self:
        for edge in self.relations:
            if edge.object == self.id:
                raise ValueError(f"node {self.id!r} has a self-edge via {edge.predicate}")
        return self

    @model_validator(mode="after")
    def _relations_are_canonical(self) -> Self:
        """Sort and de-duplicate relations at construction.

        Canonicalizing here rather than only in the emitter means the *model* is
        the canonical form, so parse(dump(x)) == x holds as an identity. It also
        catches duplicate (predicate, object) pairs, which would violate the
        index's primary key long after the file was written.
        """
        keys = [e.sort_key() for e in self.relations]
        duplicates = {k for k in keys if keys.count(k) > 1}
        if duplicates:
            listed = ", ".join(f"{p} -> {o}" for p, o in sorted(duplicates))
            raise ValueError(f"node {self.id!r} has duplicate relations: {listed}")

        ordered = tuple(sorted(self.relations, key=lambda e: e.sort_key()))
        if ordered != self.relations:
            object.__setattr__(self, "relations", ordered)
        return self


class Node(BaseModel):
    """A parsed canonical file: frontmatter plus the markdown body."""

    model_config = ConfigDict(frozen=True)

    frontmatter: Frontmatter
    body: str = Field(default="")

    @property
    def id(self) -> str:
        return self.frontmatter.id

    @property
    def type(self) -> NodeType:
        return self.frontmatter.type


# ids.TYPE_PLURALS is hand-written for import cheapness; keep it honest.
def _assert_plurals_cover_node_types() -> None:
    missing = {t.value for t in NodeType} - set(TYPE_PLURALS)
    if missing:
        raise RuntimeError(f"ids.TYPE_PLURALS is missing node types: {sorted(missing)}")


_assert_plurals_cover_node_types()
