"""One protocol, two implementations, one suite.

`MemoryIndex` filters ACLs with a Python predicate over a dict. `PostgresIndex`
pushes the same decision into SQL as a join over `(acl_ref, ceiling)` pairs.
Those are two independent implementations of invariant 5a, and the failure mode
is not a crash — it is a search that looks like it works and returns a row the
caller may not read. Nothing but running both against the same assertions keeps
them honest.

**How this suite is built.** Every expectation is an explicit literal rather than
a comparison between the two backends. Two implementations agreeing with each
other proves nothing if they are both wrong; agreeing with a written-down
expectation is the actual contract. `TestBackendsAgree` at the end adds one
direct cross-backend comparison on top, for the ACL result set specifically.

**Three tiers, because they are not equally binding:**

* **Contract** — identical on both, always. ACLs, tombstones, traversal, and the
  `get_node` round trip.
* **Ranking** — properties only. BM25 and `ts_rank_cd` are different functions
  and will not produce the same scores; asserting they do would mean either a
  permanently red suite or one weakened until it proves nothing.
* **Divergence** — differences that are legitimate (English stemming) or known
  bugs (tombstone handling), pinned so they cannot drift unnoticed.

Postgres is opt-in via `CB_TEST_DSN`; see `conftest.py`.
"""

from __future__ import annotations

import pytest

from company_brain.acl.grants import AccessFilter, GrantTable, elevate
from company_brain.index.base import Hit, Index, IndexedNode
from company_brain.schemas.acl import Principal, PrincipalKind, Sensitivity
from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance

pytestmark = pytest.mark.integration

INTERNAL = Sensitivity.INTERNAL
RESTRICTED = Sensitivity.RESTRICTED
PUBLIC = Sensitivity.PUBLIC

DOCS = "fs:corpus:docs"
COMP = "slack:channel:COMP"
OPEN = "slack:channel:GENERAL"

# A nonsense term, so ranking assertions turn on the corpus rather than on
# whatever English happens to stem to the same root.
TERM = "zephyr"


# ---- the corpus ---------------------------------------------------------

_TYPE_OF = {
    "processes": "Process",
    "people": "Person",
    "teams": "Team",
    "documents": "Document",
}


def node(
    node_id: str,
    *,
    ref: str,
    tier: Sensitivity,
    title: str = "",
    status: str = "active",
    edges: tuple[Edge, ...] = (),
) -> IndexedNode:
    return IndexedNode(
        id=node_id,
        type=_TYPE_OF[node_id.split("/", 1)[0]],
        title=title or node_id.rsplit("/", 1)[-1].replace("-", " ").capitalize(),
        acl_ref=ref,
        sensitivity=tier,
        status=status,
        content_sha256="",
        # Sorted the way `Frontmatter` canonicalises relations, so the order a
        # backend returns them in is comparable to the order we handed over.
        edges=tuple(sorted(edges, key=lambda e: e.sort_key())),
    )


# An `owns` edge naming a third party: the subject is a person, not the document
# holding the edge. `raw_subject` must survive the round trip, or traversal roots
# the triple at the wrong node.
OWNS_SAM = Edge(
    predicate=Predicate.OWNS,
    subject="people/sam-kaur",
    object="processes/vendor-renewal",
    confidence=0.91,
    provenance=Provenance.HUMAN,
    status=EdgeStatus.ACCEPTED,
    evidence=(
        Evidence(node="documents/memo", span=(4, 22), quote="Sam owns renewals"),
        Evidence(node="documents/thread", span=(0, 11)),
    ),
)

# Proposed, therefore never traversable (invariant 10).
PROPOSED_HANDOFF = Edge(
    predicate=Predicate.HANDOFF_TO,
    subject=None,
    object="teams/engineering",
    confidence=0.42,
    provenance=Provenance.LLM,
    status=EdgeStatus.PROPOSED,
    evidence=(Evidence(node="self", span=(1, 9)),),
)

MENTIONS_TOMBSTONE = Edge(
    predicate=Predicate.MENTIONS,
    subject=None,
    object="documents/deleted-memo",
    confidence=1.0,
    provenance=Provenance.STRUCTURAL,
    status=EdgeStatus.ACCEPTED,
)

# A relation the deleted document carried before it was tombstoned. The store
# keeps it so old citations still resolve; it must not be traversable, and it
# must not be counted. Without this edge the stats divergence is untestable.
DELETED_MENTIONS_SAM = Edge(
    predicate=Predicate.MENTIONS,
    subject=None,
    object="people/sam-kaur",
    confidence=1.0,
    provenance=Provenance.STRUCTURAL,
    status=EdgeStatus.ACCEPTED,
)

MENTIONS_SAM = Edge(
    predicate=Predicate.MENTIONS,
    subject=None,
    object="people/sam-kaur",
    confidence=1.0,
    provenance=Provenance.STRUCTURAL,
    status=EdgeStatus.ACCEPTED,
)

# Restricted bodies repeat the term so they outrank every visible one. That is
# what makes the LIMIT test meaningful: without it, invisible rows would not be
# competing for the slots a visible caller is entitled to.
DENSE = f"{TERM} {TERM} {TERM} {TERM} {TERM} compensation review"

CORPUS: list[tuple[IndexedNode, str]] = [
    (
        node(
            "processes/vendor-renewal",
            ref=DOCS,
            tier=INTERNAL,
            edges=(OWNS_SAM, MENTIONS_TOMBSTONE, MENTIONS_SAM, PROPOSED_HANDOFF),
        ),
        f"The {TERM} renewal process governs contract renewals.",
    ),
    (
        node("people/sam-kaur", ref=DOCS, tier=INTERNAL),
        f"Sam Kaur works on {TERM} and signs off on contracts.",
    ),
    (
        node("teams/engineering", ref=OPEN, tier=PUBLIC),
        f"Engineering handles {TERM} escalations.",
    ),
    (node("processes/comp-review-a", ref=COMP, tier=RESTRICTED), DENSE),
    (node("processes/comp-review-b", ref=COMP, tier=RESTRICTED), DENSE),
    (node("processes/comp-review-c", ref=COMP, tier=RESTRICTED), DENSE),
    (
        # Tombstoned: resolvable by id forever, never retrievable (§9.3).
        node(
            "documents/deleted-memo",
            ref=DOCS,
            tier=INTERNAL,
            status="deleted",
            edges=(DELETED_MENTIONS_SAM,),
        ),
        f"Confidential {TERM} memo that was deleted upstream.",
    ),
]

BY_ID = {n.id: n for n, _ in CORPUS}

ACTIVE_IDS = frozenset(n.id for n, _ in CORPUS if n.status == "active")
VISIBLE_TO_STAFF = frozenset({"processes/vendor-renewal", "people/sam-kaur"})
RESTRICTED_IDS = frozenset(
    {"processes/comp-review-a", "processes/comp-review-b", "processes/comp-review-c"}
)


# ---- visibilities -------------------------------------------------------


def seeing(*grants: tuple[str, Sensitivity]) -> AccessFilter:
    table = GrantTable()
    for ref, ceiling in grants:
        table.grant("p", ref, ceiling)
    return AccessFilter(table, Principal(id="p", kind=PrincipalKind.USER, display="p"))


def staff() -> AccessFilter:
    """Sees the docs corpus at internal. Not the comp channel."""
    return seeing((DOCS, INTERNAL))


def everyone() -> AccessFilter:
    return seeing((DOCS, INTERNAL), (COMP, RESTRICTED), (OPEN, PUBLIC))


def nobody() -> AccessFilter:
    return seeing()


def elevated() -> AccessFilter:
    return AccessFilter(GrantTable(), elevate())


@pytest.fixture
def populated(index: Index) -> Index:
    index.rebuild(CORPUS)
    return index


def node_ids(hits: list[Hit]) -> set[str]:
    return {h.chunk.node_id for h in hits}


# The single defect behind every cross-backend failure in this suite. It is not
# eight bugs; it is one missing line surfacing in eight places, which is exactly
# why the reason is written once and shared.
TOMBSTONE_LEAK = (
    "PostgresIndex.rebuild (postgres.py:166) has no node-status check, so a tombstoned "
    "node is chunked, embedded, indexed, and left traversable. MemoryIndex skips "
    "non-active nodes (memory.py:72). ARCHITECTURE §9.3: a tombstone stays resolvable "
    "and is never retrievable — so this leaks deleted content into search and traversal."
)


def xfail_on_tombstone_leak(backend_name: str, request: pytest.FixtureRequest) -> None:
    """Mark a test as a known Postgres failure, strictly.

    `strict=True` matters: the moment the missing status check lands, the xfail
    itself fails and forces whoever fixed it to delete this marker. A
    non-strict xfail would let the bug be fixed and the suite go on quietly
    reporting it as broken."""
    if backend_name == "postgres":
        request.applymarker(pytest.mark.xfail(strict=True, reason=TOMBSTONE_LEAK))


# ---- tier A: the contract ----------------------------------------------


class TestNodeRoundTrip:
    def test_every_node_survives_the_round_trip(self, populated: Index) -> None:
        """Including tombstones — a deleted node stays resolvable so a citation
        issued before the delete lands on "deleted on <date>" and not a dangling
        id (§9.3)."""
        for original, _ in CORPUS:
            assert populated.get_node(original.id) == original

    def test_a_third_party_subject_is_preserved(self, populated: Index) -> None:
        """`raw_subject` distinguishes "this document owns X" — nonsense — from
        "Sam owns X, and this document is the evidence"."""
        fetched = populated.get_node("processes/vendor-renewal")
        assert fetched is not None
        owns = next(e for e in fetched.edges if e.predicate is Predicate.OWNS)
        assert owns.subject == "people/sam-kaur"
        assert owns.resolve_subject("processes/vendor-renewal") == "people/sam-kaur"

    def test_evidence_spans_survive_the_round_trip(self, populated: Index) -> None:
        fetched = populated.get_node("processes/vendor-renewal")
        assert fetched is not None
        owns = next(e for e in fetched.edges if e.predicate is Predicate.OWNS)
        assert owns.evidence == OWNS_SAM.evidence

    def test_an_unknown_id_is_none(self, populated: Index) -> None:
        assert populated.get_node("people/nobody-at-all") is None


class TestAclEnforcement:
    """Invariant 5a, twice over. The Python predicate and the SQL join must
    answer the same question."""

    def test_no_grants_means_no_rows(self, populated: Index) -> None:
        """Never "no grants, therefore no filter" — that inversion is how an
        empty VALUES list turns into a full table scan."""
        assert populated.search_lexical(TERM, nobody(), 10) == []
        assert populated.search_vector(TERM, nobody(), 10) == []

    def test_a_restricted_node_never_reaches_a_principal_without_it(
        self, populated: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        xfail_on_tombstone_leak(backend_name, request)
        for hits in (
            populated.search_lexical(TERM, staff(), 20),
            populated.search_vector(TERM, staff(), 20),
        ):
            assert node_ids(hits) <= VISIBLE_TO_STAFF
            assert not node_ids(hits) & RESTRICTED_IDS

    def test_a_grant_admits_everything_below_its_ceiling(self, populated: Index) -> None:
        """Tiers are ordered: a `restricted` ceiling admits internal and public
        beneath it. Comparing loose sets instead is the cross-product bug."""
        hits = populated.search_lexical(TERM, seeing((COMP, RESTRICTED)), 20)
        assert node_ids(hits) == RESTRICTED_IDS

    def test_a_ceiling_excludes_content_above_it(self, populated: Index) -> None:
        assert populated.search_lexical(TERM, seeing((COMP, INTERNAL)), 20) == []

    def test_elevated_sees_the_whole_corpus(
        self, populated: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        xfail_on_tombstone_leak(backend_name, request)
        hits = populated.search_lexical(TERM, elevated(), 50)
        assert node_ids(hits) == ACTIVE_IDS - {"documents/deleted-memo"}

    def test_every_hit_satisfies_the_predicate_it_was_filtered_by(
        self, populated: Index
    ) -> None:
        """The invariant stated directly, rather than inferred from ids."""
        access = staff()
        for hits in (
            populated.search_lexical(TERM, access, 20),
            populated.search_vector(TERM, access, 20),
        ):
            for hit in hits:
                assert access.allows(hit.chunk.acl_ref, hit.chunk.sensitivity)


class TestLimitIsNotEatenByInvisibleRows:
    """The reason the ACL is a join and not a post-filter.

    Three restricted chunks outrank every visible one for this query. Filter
    after ranking and they consume the LIMIT, so a legitimate caller silently
    gets fewer results than they are entitled to — a permission-driven recall
    cliff that looks exactly like "there wasn't much to find" (ARCHITECTURE §6.4).
    """

    def test_lexical_returns_a_full_page_of_visible_rows(
        self, populated: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        xfail_on_tombstone_leak(backend_name, request)
        hits = populated.search_lexical(TERM, staff(), 2)
        assert len(hits) == 2
        assert node_ids(hits) <= VISIBLE_TO_STAFF

    def test_vector_returns_a_full_page_of_visible_rows(
        self, populated: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        xfail_on_tombstone_leak(backend_name, request)
        hits = populated.search_vector(TERM, staff(), 2)
        assert len(hits) == 2
        assert node_ids(hits) <= VISIBLE_TO_STAFF


class TestTraversal:
    def test_accepted_edges_traverse_in_both_directions(
        self, populated: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        xfail_on_tombstone_leak(backend_name, request)
        assert populated.neighbours("people/sam-kaur", None, 10) == ["processes/vendor-renewal"]

    def test_a_proposed_edge_is_not_traversable(self, populated: Index) -> None:
        """Invariant 10. A proposed edge is visible in the markdown and in the
        review queue, and invisible to retrieval."""
        assert "teams/engineering" not in populated.neighbours(
            "processes/vendor-renewal", None, 10
        )
        assert populated.neighbours("teams/engineering", None, 10) == []

    def test_results_are_sorted_deduplicated_and_capped(self, populated: Index) -> None:
        neighbours = populated.neighbours("processes/vendor-renewal", None, 10)
        assert neighbours == sorted(neighbours)
        assert len(neighbours) == len(set(neighbours))
        assert len(populated.neighbours("processes/vendor-renewal", None, 1)) == 1

    def test_a_predicate_filter_narrows_the_walk(
        self, populated: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        xfail_on_tombstone_leak(backend_name, request)
        assert populated.neighbours(
            "processes/vendor-renewal", frozenset({"mentions"}), 10
        ) == ["people/sam-kaur"]
        assert (
            populated.neighbours("processes/vendor-renewal", frozenset({"supersedes"}), 10)
            == []
        )


class TestStats:
    def test_node_and_chunk_counts(
        self, populated: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        xfail_on_tombstone_leak(backend_name, request)
        stats = populated.stats()
        assert stats["nodes"] == len(CORPUS)
        # One chunk per node body, minus the tombstone, which contributes none.
        assert stats["chunks"] == len(CORPUS) - 1

    def test_rebuild_reports_the_chunk_count(
        self, index: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        xfail_on_tombstone_leak(backend_name, request)
        assert index.rebuild(CORPUS) == len(CORPUS) - 1


# ---- tier B: ranking properties -----------------------------------------


class TestRankingProperties:
    """Not score equality. BM25 and `ts_rank_cd` are different functions over
    different vocabularies; only these properties are common to both."""

    def test_scores_are_non_increasing(self, populated: Index) -> None:
        for hits in (
            populated.search_lexical(TERM, everyone(), 20),
            populated.search_vector(TERM, everyone(), 20),
        ):
            assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)

    def test_filtering_only_ever_removes(self, populated: Index) -> None:
        wide = node_ids(populated.search_lexical(TERM, everyone(), 50))
        narrow = node_ids(populated.search_lexical(TERM, staff(), 50))
        assert narrow <= wide

    def test_the_densest_document_ranks_first(self, populated: Index) -> None:
        """A property both scoring functions agree on: more occurrences of the
        query term in a similar-length document ranks higher."""
        top = populated.search_lexical(TERM, everyone(), 1)
        assert top and top[0].chunk.node_id in RESTRICTED_IDS

    def test_hits_carry_their_source_label(self, populated: Index) -> None:
        assert all(h.source == "lexical" for h in populated.search_lexical(TERM, everyone(), 5))
        assert all(h.source == "vector" for h in populated.search_vector(TERM, everyone(), 5))


# ---- tier C: divergences, pinned ----------------------------------------


class TestKnownDivergences:
    """Differences that are real. Written down so they cannot drift silently,
    and so that closing one forces a deliberate edit here."""

    def test_tombstoned_text_is_never_retrievable(
        self, populated: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        """§9.3: a tombstone is resolvable, never retrievable.

        `MemoryIndex` skips non-active nodes when chunking (`memory.py:72`).
        `PostgresIndex.rebuild` has no such check, so deleted content is indexed
        and searchable — a content leak, not a formatting difference.
        """
        xfail_on_tombstone_leak(backend_name, request)
        hits = populated.search_lexical("confidential", elevated(), 20)
        assert "documents/deleted-memo" not in node_ids(hits)

    def test_traversal_does_not_walk_into_a_tombstone(
        self, populated: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        """Inbound edges to a tombstone are kept in the store on purpose, but a
        graph walk must not surface deleted content. `MemoryIndex` checks the
        *target's* status (`memory.py:155`); the Postgres SQL never joins nodes.
        """
        xfail_on_tombstone_leak(backend_name, request)
        assert "documents/deleted-memo" not in populated.neighbours(
            "processes/vendor-renewal", None, 10
        )

    def test_edge_count_excludes_tombstoned_nodes(
        self, populated: Index, backend_name: str, request: pytest.FixtureRequest
    ) -> None:
        """Follows from the same root cause: MemoryIndex never records edges for
        a non-active node, Postgres inserts them regardless."""
        xfail_on_tombstone_leak(backend_name, request)
        assert populated.stats()["edges"] == 3

    def test_term_vocabulary_is_backend_specific(
        self, populated: Index, backend_name: str
    ) -> None:
        """**Legitimate**, not a bug. `tokenize()` keeps literal words; the
        Postgres `tsv` applies English stemming and drops stopwords. So the two
        term counts differ by design and `stats()['terms']` is a diagnostic, not
        a contract. Asserted as a shape so a swing still shows up."""
        assert populated.stats()["terms"] > 0

    def test_stopword_handling_differs(self, populated: Index, backend_name: str) -> None:
        """`the` is a real token in the memory postings list and a dropped
        stopword in Postgres. A query of nothing but stopwords therefore hits in
        one and not the other."""
        hits = populated.search_lexical("the", everyone(), 10)
        if backend_name == "postgres":
            assert hits == []
        else:
            assert hits != []


# ---- one direct cross-backend comparison --------------------------------


class TestBackendsAgree:
    """Everything above pins each backend to a written expectation. This asks
    the narrower question directly: given one visibility, do both return the
    same rows? It needs both backends at once, so it sits outside the fixture."""

    @pytest.mark.xfail(strict=True, reason=TOMBSTONE_LEAK)
    def test_the_visible_chunk_set_is_identical(self, migrated_dsn: str) -> None:
        from company_brain.index.base import HashingEmbedder
        from company_brain.index.memory import MemoryIndex
        from company_brain.index.postgres import PostgresIndex

        memory = MemoryIndex(HashingEmbedder())
        memory.rebuild(CORPUS)

        with PostgresIndex(migrated_dsn, HashingEmbedder()) as postgres:
            postgres.rebuild(CORPUS)
            for access in (staff(), everyone(), seeing((COMP, RESTRICTED)), nobody()):
                assert {h.chunk.id for h in memory.search_lexical(TERM, access, 50)} == {
                    h.chunk.id for h in postgres.search_lexical(TERM, access, 50)
                }, f"backends disagree on what {access.principal.id!r} may see"
