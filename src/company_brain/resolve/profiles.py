"""The per-entity view layer 3 scores against.

Built in a single `Repository.walk()` pass, because the alternative — asking the
store a question per candidate pair — turns a blocked comparison into a full
scan and gives back the quadratic cost blocking exists to avoid.

Everything an entity knows about itself comes from its own node (title,
aliases). Everything it knows about its *context* comes from the documents that
point at it: which documents, in which channels, alongside whom, and when.
Those are the four features §10.1 asks for, and all four are derivable from
accepted edges alone — so the profile is rebuildable from markdown like
everything else (invariant 2).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from company_brain.resolve.keys import identity_keys
from company_brain.schemas.edges import EdgeStatus
from company_brain.schemas.nodes import Node, NodeStatus, NodeType
from company_brain.store.repository import Repository

# Layer 3 runs over entities that source systems actually name. Process and
# Decision are excluded on purpose: §10.3 says their names are invented by the
# extractor, so string and co-occurrence features over them measure the model's
# phrasing variance rather than identity. They need clustering plus a human
# naming pass, which is a different algorithm — see the module note in
# `resolver.py`.
RESOLVABLE_TYPES: tuple[NodeType, ...] = (
    NodeType.PERSON,
    NodeType.ACCOUNT,
    NodeType.TEAM,
    NodeType.TOOL,
)


@dataclass(frozen=True, slots=True)
class EntityProfile:
    """One entity, plus the context the scorer needs. Every collection sorted."""

    node_id: str
    node_type: NodeType
    title: str
    aliases: tuple[str, ...]
    identity_keys: tuple[str, ...]
    mentioned_in: tuple[str, ...]
    channels: tuple[str, ...]
    neighbours: tuple[str, ...]
    first_seen: datetime | None = None
    last_seen: datetime | None = None

    @property
    def surfaces(self) -> tuple[str, ...]:
        """Every string that refers to this entity, title first."""
        return (self.title, *self.aliases)

    @property
    def evidence_weight(self) -> int:
        """How much the graph has to say about this entity.

        Decides which side of a merge survives, so it is a count of documents
        rather than anything derived from the node's own text — a duplicate
        with a longer alias list is not the more canonical record.
        """
        return len(self.mentioned_in)


@dataclass(slots=True)
class _Context:
    documents: list[str]
    channels: list[str]
    neighbours: list[str]
    stamps: list[datetime]


def _document_time(node: Node) -> datetime | None:
    stamps = node.frontmatter.timestamps
    return stamps.created or stamps.modified


def _endpoints(node: Node) -> tuple[str, ...]:
    """Entity IDs an accepted edge on this document points at, both ends.

    Both ends matter: ``Owen --owns--> capacity-planning`` lives on the
    document that reports it, so the subject is as much a mention of Owen as
    the object is of the process (see the `Edge.subject` docstring).
    """
    out: list[str] = []
    for edge in node.frontmatter.relations:
        if edge.status is not EdgeStatus.ACCEPTED:
            continue
        for endpoint in (edge.object, edge.resolve_subject(node.id)):
            if endpoint != node.id:
                out.append(endpoint)
    return tuple(out)


def build_profiles(
    repo: Repository, *, types: Iterable[NodeType] = RESOLVABLE_TYPES
) -> tuple[EntityProfile, ...]:
    """Profile every resolvable, active entity in the store.

    Merged and deleted nodes are skipped: a node that already redirects
    somewhere is not a candidate for a second merge, and including it would let
    layer 3 propose chains that `Repository.resolve` then has to walk.
    """
    wanted = tuple(types)
    entities: dict[str, Node] = {}
    documents: list[Node] = []

    for node in repo.walk():
        fm = node.frontmatter
        if fm.status is not NodeStatus.ACTIVE:
            continue
        if fm.type is NodeType.DOCUMENT:
            documents.append(node)
        elif fm.type in wanted:
            entities[node.id] = node

    context: dict[str, _Context] = {
        node_id: _Context([], [], [], []) for node_id in sorted(entities)
    }

    for document in documents:
        endpoints = [e for e in _endpoints(document) if e in entities]
        if not endpoints:
            continue
        when = _document_time(document)
        for endpoint in endpoints:
            found = context[endpoint]
            found.documents.append(document.id)
            found.channels.append(document.frontmatter.acl.ref)
            found.neighbours.extend(other for other in endpoints if other != endpoint)
            if when is not None:
                found.stamps.append(when)

    return tuple(_profile(entities[node_id], context[node_id]) for node_id in sorted(entities))


def _profile(node: Node, context: _Context) -> EntityProfile:
    fm = node.frontmatter
    stamps = sorted(context.stamps)
    return EntityProfile(
        node_id=node.id,
        node_type=fm.type,
        title=fm.title,
        aliases=tuple(sorted(set(fm.aliases))),
        identity_keys=identity_keys((fm.title, *fm.aliases)),
        mentioned_in=tuple(sorted(set(context.documents))),
        channels=tuple(sorted(set(context.channels))),
        neighbours=tuple(sorted(set(context.neighbours))),
        first_seen=stamps[0] if stamps else None,
        last_seen=stamps[-1] if stamps else None,
    )
