"""One conformance suite, two index backends.

`MemoryIndex` and `PostgresIndex` implement the same protocol and are trivially
easy to let drift — the in-memory one is what CI exercises on every run, and the
Postgres one is what production would actually serve. Anything asserted here is
asserted about both.

What is deliberately *not* asserted: score values. BM25 and `ts_rank_cd` are
different functions and will never agree numerically. The contract is which rows
come back, in what order relative to each other, and — above all — which rows do
not come back at all.
"""

from __future__ import annotations

from typing import Any

import pytest

from company_brain.acl.grants import AccessFilter, GrantTable, elevate
from company_brain.index.base import IndexedNode
from company_brain.schemas.acl import Principal, PrincipalKind, Sensitivity
from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance

INTERNAL = Sensitivity.INTERNAL
RESTRICTED = Sensitivity.RESTRICTED
PUBLIC = Sensitivity.PUBLIC

OPEN_REF = "fs:corpus:docs"
VAULT_REF = "slack:channel:VAULT"
MIXED_REF = "gdrive:folder:MIXED"

VENDOR = "processes/vendor-renewal"
COMP = "processes/executive-compensation"
MIXED_LOW = "documents/mixed-internal"
MIXED_HIGH = "documents/mixed-restricted"
OWNER = "people/sam-kaur"


def human(name: str) -> Principal:
    return Principal(id=name, kind=PrincipalKind.USER, display=name)


def node(
    node_id: str,
    title: str,
    ref: str,
    tier: Sensitivity,
    *,
    edges: tuple[Edge, ...] = (),
    node_type: str = "Process",
) -> IndexedNode:
    return IndexedNode(
        id=node_id,
        type=node_type,
        title=title,
        acl_ref=ref,
        sensitivity=tier,
        status="active",
        content_sha256="0" * 64,
        edges=edges,
    )


def corpus() -> list[tuple[IndexedNode, str]]:
    """Four nodes chosen so that every ACL mistake shows up as a failure.

    `vendor renewal` and `executive compensation` share vocabulary, so a query
    that should only reach the open node will reach the restricted one too if the
    filter is missing. The two MIXED nodes share a ref and differ only in tier,
    which is the case a ref-only filter gets wrong.
    """
    owns = Edge(
        predicate=Predicate.OWNS,
        subject=OWNER,
        object=VENDOR,
        confidence=0.9,
        provenance=Provenance.LLM,
        status=EdgeStatus.ACCEPTED,
        evidence=(Evidence(node="self", span=(0, 12), quote="Sam Kaur owns"),),
    )
    mentions = Edge(
        predicate=Predicate.MENTIONS,
        object=OWNER,
        confidence=0.5,
        provenance=Provenance.STRUCTURAL,
        status=EdgeStatus.ACCEPTED,
    )
    proposed = Edge(
        predicate=Predicate.DEPENDS_ON,
        object=COMP,
        confidence=0.4,
        provenance=Provenance.LLM,
        status=EdgeStatus.PROPOSED,
        evidence=(Evidence(node="self", quote="budget is set against"),),
    )
    return [
        (
            node(
                VENDOR, "Vendor renewal", OPEN_REF, INTERNAL, edges=(owns, mentions, proposed)
            ),
            "# Vendor renewal\n\nSam Kaur owns vendor renewal and signs every contract.\n"
            "Renewals are tracked quarterly against the procurement calendar.",
        ),
        (
            node(COMP, "Executive compensation", VAULT_REF, RESTRICTED),
            "# Executive compensation\n\nCompensation bands for the leadership team.\n"
            "The vendor renewal budget is set against the compensation pool.",
        ),
        (
            node(MIXED_LOW, "Procurement handbook", MIXED_REF, INTERNAL, node_type="Document"),
            "# Procurement handbook\n\nThe handbook covers routine purchasing thresholds.",
        ),
        (
            node(MIXED_HIGH, "Acquisition memo", MIXED_REF, RESTRICTED, node_type="Document"),
            "# Acquisition memo\n\nThe memo covers an unannounced purchasing decision.",
        ),
        (
            node(OWNER, "Sam Kaur", OPEN_REF, INTERNAL, node_type="Person"),
            "Sam Kaur leads procurement.",
        ),
    ]


def grants_for(*, mixed_ceiling: Sensitivity | None = INTERNAL) -> GrantTable:
    table = GrantTable()
    table.grant("reader", OPEN_REF, INTERNAL)
    if mixed_ceiling is not None:
        table.grant("reader", MIXED_REF, mixed_ceiling)
    table.grant("boss", OPEN_REF, INTERNAL)
    table.grant("boss", VAULT_REF, RESTRICTED)
    table.grant("boss", MIXED_REF, RESTRICTED)
    return table


def node_ids(hits: list[Any]) -> set[str]:
    return {h.chunk.node_id for h in hits}


class IndexConformance:
    """Subclass and provide an `index` fixture returning a freshly built index."""

    @pytest.fixture
    def index(self) -> Any:  # pragma: no cover - overridden
        raise NotImplementedError

    @pytest.fixture
    def built(self, index: Any) -> Any:
        index.rebuild(corpus())
        return index

    @staticmethod
    def access(who: str, table: GrantTable | None = None) -> AccessFilter:
        return AccessFilter(table or grants_for(), human(who))

    # ---- shape -----------------------------------------------------------

    def test_rebuild_returns_the_chunk_count(self, index: Any) -> None:
        assert index.rebuild(corpus()) == index.stats()["chunks"] > 0

    def test_stats_reports_the_four_counters(self, built: Any) -> None:
        stats = built.stats()
        assert set(stats) == {"nodes", "chunks", "terms", "edges"}
        assert stats["nodes"] == len(corpus())
        # Two accepted edges on the vendor node; the proposed one is not counted.
        assert stats["edges"] == 2
        assert stats["terms"] > 0

    def test_rebuild_is_repeatable(self, built: Any) -> None:
        """Invariant 2 in miniature: the index is a function of its input."""
        before = built.stats()
        built.rebuild(corpus())
        assert built.stats() == before

    def test_rebuild_drops_what_is_no_longer_in_the_store(self, built: Any) -> None:
        built.rebuild(corpus()[:1])
        assert built.stats()["nodes"] == 1
        assert built.get_node(COMP) is None

    # ---- get_node --------------------------------------------------------

    def test_get_node_round_trips(self, built: Any) -> None:
        got = built.get_node(VENDOR)
        assert got is not None
        assert (got.id, got.type, got.title) == (VENDOR, "Process", "Vendor renewal")
        assert (got.acl_ref, got.sensitivity) == (OPEN_REF, INTERNAL)
        assert got.status == "active"

    def test_get_node_preserves_every_edge_including_undecided_ones(self, built: Any) -> None:
        """The review queue reads proposed edges back out of the graph, so an
        index that kept only the traversable ones would hide the queue."""
        got = built.get_node(VENDOR)
        assert got is not None
        by_predicate = {str(e.predicate): e for e in got.edges}
        assert set(by_predicate) == {"owns", "mentions", "depends_on"}
        assert by_predicate["depends_on"].status is EdgeStatus.PROPOSED
        # An explicit subject must survive: `owns` is rooted at the person.
        assert by_predicate["owns"].subject == OWNER
        assert by_predicate["mentions"].subject is None
        assert by_predicate["owns"].evidence[0].quote == "Sam Kaur owns"
        assert by_predicate["owns"].evidence[0].span == (0, 12)

    def test_get_node_is_none_for_a_stranger(self, built: Any) -> None:
        assert built.get_node("processes/does-not-exist") is None

    # ---- search: the ACL contract ---------------------------------------

    def test_lexical_finds_what_the_principal_may_see(self, built: Any) -> None:
        hits = built.search_lexical("vendor renewal", self.access("reader"), 10)
        assert VENDOR in node_ids(hits)

    def test_lexical_never_returns_an_invisible_node(self, built: Any) -> None:
        """Both documents talk about vendor renewal; only one is grantable."""
        hits = built.search_lexical("vendor renewal", self.access("reader"), 10)
        assert COMP not in node_ids(hits)

    def test_vector_never_returns_an_invisible_node(self, built: Any) -> None:
        hits = built.search_vector("compensation bands", self.access("reader"), 10)
        assert COMP not in node_ids(hits)

    def test_the_boss_can_reach_the_restricted_node(self, built: Any) -> None:
        """The canary must be reachable by someone, or the tests above pass
        trivially and prove nothing."""
        hits = built.search_lexical("compensation", self.access("boss"), 10)
        assert COMP in node_ids(hits)

    def test_a_ceiling_is_per_ref_not_per_principal(self, built: Any) -> None:
        """Invariant 5a at the index layer. `reader` holds MIXED_REF at internal;
        the restricted document under the same ref must stay invisible."""
        access = self.access("reader")
        hits = built.search_lexical("purchasing", access, 10)
        assert MIXED_LOW in node_ids(hits)
        assert MIXED_HIGH not in node_ids(hits)

    def test_raising_the_ceiling_on_one_ref_reveals_only_that_ref(self, built: Any) -> None:
        access = self.access("reader", grants_for(mixed_ceiling=RESTRICTED))
        found = node_ids(built.search_lexical("purchasing", access, 10))
        assert {MIXED_LOW, MIXED_HIGH} <= found
        # Still no reach into the vault: a raised ceiling is not a wider grant.
        assert COMP not in node_ids(built.search_lexical("compensation", access, 10))

    def test_a_principal_with_no_grants_sees_nothing(self, built: Any) -> None:
        access = AccessFilter(GrantTable(), human("stranger"))
        assert built.search_lexical("vendor renewal", access, 10) == []
        assert built.search_vector("vendor renewal", access, 10) == []

    def test_an_elevated_filter_sees_everything(self, built: Any) -> None:
        """The rebuild path reads every node; it must not be filtered."""
        access = AccessFilter(GrantTable(), elevate())
        assert COMP in node_ids(built.search_lexical("compensation", access, 10))

    def test_the_acl_filter_applies_before_the_limit(self, built: Any) -> None:
        """A post-filter would spend the LIMIT on rows the caller cannot see and
        return fewer results than it should — a silent recall cliff (§6.4)."""
        access = self.access("reader")
        hits = built.search_lexical("purchasing handbook memo", access, 1)
        assert len(hits) == 1
        assert MIXED_HIGH not in node_ids(hits)

    def test_limit_is_honoured(self, built: Any) -> None:
        assert (
            len(
                built.search_lexical("renewal procurement compensation", self.access("boss"), 2)
            )
            <= 2
        )

    def test_an_empty_query_returns_nothing(self, built: Any) -> None:
        assert built.search_lexical("   ", self.access("boss"), 5) == []

    # ---- traversal -------------------------------------------------------

    def test_neighbours_walks_both_directions(self, built: Any) -> None:
        """`owns` is stored as person -> process; both ends must find each other."""
        assert VENDOR in built.neighbours(OWNER, None, 10)
        assert OWNER in built.neighbours(VENDOR, None, 10)

    def test_neighbours_ignores_undecided_edges(self, built: Any) -> None:
        """Invariant 10: only accepted edges are traversed at query time."""
        assert COMP not in built.neighbours(VENDOR, None, 10)

    def test_neighbours_filters_by_predicate(self, built: Any) -> None:
        assert built.neighbours(OWNER, frozenset({"owns"}), 10) == [VENDOR]
        assert built.neighbours(OWNER, frozenset({"handoff_to"}), 10) == []

    def test_neighbours_is_deterministic_and_bounded(self, built: Any) -> None:
        got = built.neighbours(VENDOR, None, 1)
        assert got == sorted(got)
        assert len(got) <= 1
