"""A tombstoned node is resolvable but never retrievable.

The §14 Q3 decision — purge the body by default, retain the graph always, retain
the body only under an explicit per-connector opt-in — is only safe if deleted
content cannot reach an answer. Before these tests, it could: MemoryIndex
indexed every node it was handed and filtered edges by EdgeStatus, never
NodeStatus, and AccessFilter checks ACL and sensitivity, not status.

That made `retain_content=False` load-bearing by accident. It was the only
reason deleted text stayed out of answers, so the first opt-in retention path
would have shipped a leak with nothing to catch it.

The contract these pin:
  resolvable    get_node returns it, so a citation issued before the delete
                resolves to "deleted on <date>" rather than a dangling id
  unretrievable no chunks, so never a search hit; never expanded into by a
                graph walk; rejected by the citation validator
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from company_brain.acl.grants import AccessFilter, GrantTable
from company_brain.index.base import IndexedNode
from company_brain.index.memory import MemoryIndex
from company_brain.retrieve.hybrid import HybridRetriever
from company_brain.schemas.acl import Principal, PrincipalKind, Sensitivity
from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance
from company_brain.schemas.nodes import NodeStatus
from company_brain.synthesize.answer import Answer, UncitedAnswerError, validate

INTERNAL = Sensitivity.INTERNAL
REF = "fs:corpus:docs"
LIVE = "documents/live-000001"
GONE = "documents/gone-000002"
SECRET_TEXT = "The renewal price is 240000 dollars, negotiated by Sam Kaur."


def node(
    node_id: str, title: str, status: NodeStatus, edges: tuple[Edge, ...] = ()
) -> IndexedNode:
    return IndexedNode(
        id=node_id,
        type="Document",
        title=title,
        acl_ref=REF,
        sensitivity=INTERNAL,
        status=str(status),
        content_sha256="a" * 64,
        edges=edges,
    )


@pytest.fixture
def index() -> MemoryIndex:
    """One live node and one tombstone whose body was *retained* — the opt-in
    path. If retention is safe, this must still never surface."""
    idx = MemoryIndex()
    link = Edge(
        predicate=Predicate.MENTIONS,
        object=GONE,
        confidence=1.0,
        provenance=Provenance.HUMAN,
        status=EdgeStatus.ACCEPTED,
        evidence=(Evidence(span=(0, 4)),),
    )
    idx.rebuild(
        [
            (node(LIVE, "Live doc", NodeStatus.ACTIVE, (link,)), "Vendor renewal notes."),
            (node(GONE, "Deleted doc", NodeStatus.DELETED), SECRET_TEXT),
        ]
    )
    return idx


@pytest.fixture
def access() -> AccessFilter:
    grants = GrantTable()
    grants.grant("reader", REF, INTERNAL)
    return AccessFilter(
        grants, Principal(id="reader", kind=PrincipalKind.USER, display="Reader")
    )


class TestResolvable:
    def test_a_tombstone_is_still_resolvable_by_id(self, index: MemoryIndex) -> None:
        # Invariant 12: an answer issued before the delete must not dangle.
        indexed = index.get_node(GONE)
        assert indexed is not None
        assert indexed.status == str(NodeStatus.DELETED)


class TestUnretrievable:
    def test_a_tombstone_is_never_a_search_hit(
        self, index: MemoryIndex, access: AccessFilter
    ) -> None:
        for query in ("renewal price", "negotiated by Sam Kaur", "240000"):
            hits = index.search_lexical(query, access, 10) + index.search_vector(
                query, access, 10
            )
            assert not [h for h in hits if h.chunk.node_id == GONE], query

    def test_retained_body_is_not_chunked(self, index: MemoryIndex) -> None:
        """The opt-in retention path stores the text but must not index it."""
        assert index.stats()["nodes"] == 2
        assert all(c.node_id != GONE for c in index._chunks.values())

    def test_a_graph_walk_does_not_expand_into_a_tombstone(self, index: MemoryIndex) -> None:
        # The inbound edge survives in the store, but traversal must not follow it.
        assert GONE not in index.neighbours(LIVE, None, limit=10)

    def test_retrieval_never_returns_a_tombstone(
        self, index: MemoryIndex, access: AccessFilter
    ) -> None:
        result = HybridRetriever(index, access).retrieve("renewal price", limit=10)
        assert all(n.node_id != GONE for n in result.nodes)


class TestCitationRefusesDeletedSources:
    def test_citing_a_tombstone_is_refused(
        self, index: MemoryIndex, access: AccessFilter
    ) -> None:
        """The answer must not ship. Note *which* check fires: retrieval already
        excluded the tombstone, so the fabricated-citation check catches it
        first. That is the layering working — the status check below is the
        second line, not the first."""
        retrieval = HybridRetriever(index, access).retrieve("renewal", limit=10)
        forged = Answer(
            question="what was the price?",
            text=f"The renewal price was 240000 dollars. [[{GONE}]]",
        )
        with pytest.raises(UncitedAnswerError, match="fabricated citation"):
            validate(forged, retrieval, access, index)

    def test_the_status_check_fires_if_a_tombstone_reaches_the_context(
        self, index: MemoryIndex, access: AccessFilter
    ) -> None:
        """Directly exercises the second line of defence.

        Simulates the index and store disagreeing — a tombstone present in the
        retrieved context. Retrieval should never produce this; if it ever does,
        the answer still must not ship.
        """
        from company_brain.retrieve.hybrid import Retrieval, RetrievedNode

        contaminated = Retrieval(
            query="price",
            nodes=[RetrievedNode(node_id=GONE, title="Deleted doc", score=1.0)],
            seed_count=1,
            expanded_count=0,
            filtered_out=0,
        )
        forged = Answer(
            question="what was the price?",
            text=f"The renewal price was 240000 dollars. [[{GONE}]]",
        )
        with pytest.raises(UncitedAnswerError, match="deleted upstream"):
            validate(forged, contaminated, access, index)


class TestRetentionIsNowSafe:
    def test_retained_and_purged_tombstones_are_equally_unretrievable(
        self, access: AccessFilter
    ) -> None:
        """The point of the whole exercise: whether the body was kept must make
        no difference to what an answer can see. Until it didn't, `retain_content`
        was a safety mechanism rather than a policy choice."""
        results = []
        for body in (SECRET_TEXT, "_deleted upstream on 2024-06-01._"):
            idx = MemoryIndex()
            idx.rebuild([(node(GONE, "Deleted", NodeStatus.DELETED), body)])
            results.append(
                [h.chunk.node_id for h in idx.search_lexical("renewal price", access, 10)]
            )
        assert results[0] == results[1] == []


class TestTombstoneWriting:
    def test_tombstone_preserves_the_graph(self) -> None:
        """Retain the graph always. The extracted claims are where the "why did
        we decide X" value lives, not the body — which is what makes purging the
        body cheap."""
        from company_brain.schemas.acl import AclRef
        from company_brain.schemas.nodes import Frontmatter, Node, NodeType, SourceRef
        from company_brain.store.backend import MemoryBackend
        from company_brain.store.repository import Repository

        repo = Repository(MemoryBackend())
        edge = Edge(
            predicate=Predicate.OWNS,
            subject="people/sam-kaur",
            object="processes/vendor-renewal",
            confidence=0.9,
            provenance=Provenance.LLM,
            status=EdgeStatus.PROPOSED,
            evidence=(Evidence(span=(0, 10), quote="Sam owns it"),),
        )
        repo.put(
            Node(
                frontmatter=Frontmatter(
                    id=GONE,
                    type=NodeType.DOCUMENT,
                    title="Decision",
                    acl=AclRef(ref=REF, sensitivity=INTERNAL),
                    source=SourceRef(
                        connector="t", uri="u", external_id="e", content_sha256="a" * 64
                    ),
                    relations=(edge,),
                ),
                body=SECRET_TEXT,
            )
        )
        out = repo.tombstone(
            GONE, deleted_at=datetime(2024, 6, 1, tzinfo=UTC), retain_content=False
        )
        assert SECRET_TEXT not in out.body
        assert out.frontmatter.relations == (edge,)
        assert out.frontmatter.relations[0].subject == "people/sam-kaur"
