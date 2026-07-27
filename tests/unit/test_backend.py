"""Backend conformance suite plus fence and repository tests.

The conformance class runs against every backend so behaviour can't drift
between dev and prod. SupabaseStorageBackend joins it under an `integration`
mark once there's a live stack to point at.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from company_brain.schemas.acl import AclRef, Sensitivity
from company_brain.schemas.nodes import Frontmatter, Node, NodeStatus, NodeType
from company_brain.store.backend import (
    LocalFsBackend,
    MemoryBackend,
    StoreBackend,
    StorePathError,
    TieredBackend,
    safe_relpath,
    tier_root,
)
from company_brain.store.fences import (
    FenceError,
    RegionTampered,
    find_regions,
    get_region,
    human_content_hash,
    region_hash,
    render_fence,
    strip_regions,
    upsert_region,
)
from company_brain.store.repository import (
    TIER_ORDER,
    AclWideningError,
    DuplicateNodeError,
    NodeNotFoundError,
    Repository,
    StoreError,
    TierMismatchError,
)


@pytest.fixture(params=["memory", "localfs"])
def backend(request: pytest.FixtureRequest, tmp_path: Path) -> StoreBackend:
    if request.param == "memory":
        return MemoryBackend()
    return LocalFsBackend(tmp_path)


class TestBackendConformance:
    def test_absent_read_returns_none(self, backend: StoreBackend) -> None:
        assert backend.read_text("people/nobody.md") is None

    def test_write_then_read(self, backend: StoreBackend) -> None:
        backend.write_text("people/sam-kaur.md", "hello")
        assert backend.read_text("people/sam-kaur.md") == "hello"

    def test_write_is_idempotent_and_overwrites(self, backend: StoreBackend) -> None:
        backend.write_text("a/b.md", "one")
        backend.write_text("a/b.md", "two")
        assert backend.read_text("a/b.md") == "two"

    def test_exists(self, backend: StoreBackend) -> None:
        assert not backend.exists("a/b.md")
        backend.write_text("a/b.md", "x")
        assert backend.exists("a/b.md")

    def test_delete_reports_whether_it_removed_anything(self, backend: StoreBackend) -> None:
        assert backend.delete("a/b.md") is False
        backend.write_text("a/b.md", "x")
        assert backend.delete("a/b.md") is True
        assert backend.read_text("a/b.md") is None

    def test_walk_is_sorted(self, backend: StoreBackend) -> None:
        for name in ("c", "a", "b"):
            backend.write_text(f"people/{name}.md", "x")
        walked = list(backend.walk("people"))
        assert walked == sorted(walked)
        assert walked == ["people/a.md", "people/b.md", "people/c.md"]

    def test_walk_respects_prefix(self, backend: StoreBackend) -> None:
        backend.write_text("people/a.md", "x")
        backend.write_text("teams/b.md", "x")
        assert list(backend.walk("people")) == ["people/a.md"]

    def test_walk_empty_prefix_yields_nothing(self, backend: StoreBackend) -> None:
        assert list(backend.walk("people")) == []

    def test_unicode_survives_round_trip(self, backend: StoreBackend) -> None:
        backend.write_text("a/b.md", "Zoë — naïve café 🙂")
        assert backend.read_text("a/b.md") == "Zoë — naïve café 🙂"

    @pytest.mark.parametrize(
        "bad",
        ["/etc/passwd", "../outside.md", "a/../../b.md", "", ".", "a\\b.md", "a\x00b"],
    )
    def test_unsafe_paths_rejected(self, backend: StoreBackend, bad: str) -> None:
        with pytest.raises(StorePathError):
            backend.write_text(bad, "x")


class TestPathSafety:
    def test_normalizes_redundant_segments(self) -> None:
        assert str(safe_relpath("a/./b.md")) == "a/b.md"

    def test_localfs_write_stays_inside_root(self, tmp_path: Path) -> None:
        root = tmp_path / "store"
        root.mkdir()
        outside = tmp_path / "escaped.md"
        backend = LocalFsBackend(root)
        with pytest.raises(StorePathError):
            backend.write_text("../escaped.md", "pwned")
        assert not outside.exists()

    def test_localfs_rejects_symlink_escape(self, tmp_path: Path) -> None:
        root = tmp_path / "store"
        root.mkdir()
        (tmp_path / "elsewhere").mkdir()
        (root / "link").symlink_to(tmp_path / "elsewhere")
        with pytest.raises(StorePathError):
            LocalFsBackend(root).write_text("link/pwned.md", "x")

    def test_localfs_leaves_no_temp_files_behind(self, tmp_path: Path) -> None:
        backend = LocalFsBackend(tmp_path)
        backend.write_text("a/b.md", "x")
        assert [p.name for p in (tmp_path / "a").iterdir()] == ["b.md"]


class TestFences:
    def test_render_and_parse_round_trip(self) -> None:
        body = render_fence("mentions", "Mentioned in 34 documents.")
        regions = find_regions(body)
        assert len(regions) == 1
        assert regions[0].name == "mentions"
        assert regions[0].content == "Mentioned in 34 documents."
        assert regions[0].is_intact

    def test_hash_ignores_surrounding_blank_lines(self) -> None:
        assert region_hash("text") == region_hash("\n\ntext\n\n")

    def test_human_text_outside_fences_is_preserved(self) -> None:
        body = "Joined 2021. Owns the vendor lifecycle.\n\n" + render_fence("mentions", "old")
        updated = upsert_region(body, "mentions", "new")
        assert "Joined 2021. Owns the vendor lifecycle." in updated
        assert get_region(updated, "mentions") is not None
        assert get_region(updated, "mentions").content == "new"  # type: ignore[union-attr]

    def test_edit_inside_a_region_blocks_the_write(self) -> None:
        body = render_fence("mentions", "generated text")
        tampered = body.replace("generated text", "a human wrote this")
        with pytest.raises(RegionTampered) as caught:
            upsert_region(tampered, "mentions", "regenerated")
        assert caught.value.region == "mentions"

    def test_force_overrides_tampering_for_the_review_path(self) -> None:
        body = render_fence("mentions", "generated")
        tampered = body.replace("generated", "human edit")
        assert "regenerated" in upsert_region(tampered, "mentions", "regenerated", force=True)

    def test_upsert_appends_when_region_absent(self) -> None:
        updated = upsert_region("Human prose.", "mentions", "generated")
        assert updated.startswith("Human prose.")
        assert get_region(updated, "mentions") is not None

    def test_repeated_upsert_of_same_content_is_stable(self) -> None:
        # Determinism: an unchanged regeneration must produce a zero-line diff.
        once = upsert_region("Human prose.", "mentions", "generated")
        assert upsert_region(once, "mentions", "generated") == once

    def test_multiple_regions_are_independent(self) -> None:
        body = render_fence("a", "one") + "\n\n" + render_fence("b", "two")
        updated = upsert_region(body, "a", "ONE")
        assert get_region(updated, "a").content == "ONE"  # type: ignore[union-attr]
        assert get_region(updated, "b").content == "two"  # type: ignore[union-attr]

    def test_unbalanced_fences_rejected(self) -> None:
        with pytest.raises(FenceError, match="unbalanced"):
            find_regions("<!-- cb:generated start region=a hash=deadbeef -->\nx\n")

    def test_mismatched_fence_names_rejected(self) -> None:
        body = (
            "<!-- cb:generated start region=a hash=deadbeef -->\nx\n"
            "<!-- cb:generated end region=b -->\n"
        )
        with pytest.raises(FenceError, match="closed by"):
            find_regions(body)

    def test_duplicate_region_names_rejected(self) -> None:
        body = render_fence("a", "one") + "\n" + render_fence("a", "two")
        with pytest.raises(FenceError, match="duplicate region"):
            find_regions(body)

    def test_invalid_region_name_rejected(self) -> None:
        with pytest.raises(FenceError, match="invalid region name"):
            render_fence("Mentions Section", "x")

    def test_strip_regions_leaves_only_human_text(self) -> None:
        body = "Before.\n\n" + render_fence("a", "generated") + "\n\nAfter."
        assert strip_regions(body) == "Before.\n\nAfter."

    def test_human_hash_unchanged_by_regeneration(self) -> None:
        # An ingest run must be able to tell its own regeneration apart from a
        # person's edit without diffing the whole tree.
        body = "Human prose.\n\n" + render_fence("a", "v1")
        regenerated = upsert_region(body, "a", "v2 completely different")
        assert human_content_hash(body) == human_content_hash(regenerated)

    def test_human_hash_changes_when_a_person_edits(self) -> None:
        body = "Human prose.\n\n" + render_fence("a", "v1")
        edited = body.replace("Human prose.", "Human prose, revised.")
        assert human_content_hash(body) != human_content_hash(edited)


def person(node_id: str, tier: Sensitivity = Sensitivity.INTERNAL) -> Node:
    return Node(
        frontmatter=Frontmatter(
            id=node_id,
            type=NodeType.PERSON,
            title=node_id.split("/")[-1],
            acl=AclRef(ref="fs:corpus:main", sensitivity=tier),
        ),
        body="",
    )


@pytest.fixture
def repo() -> Repository:
    return Repository(MemoryBackend())


class TestRepository:
    def test_put_then_get(self, repo: Repository) -> None:
        repo.put(person("people/sam-kaur"))
        assert repo.get("people/sam-kaur").id == "people/sam-kaur"

    def test_missing_node_raises(self, repo: Repository) -> None:
        with pytest.raises(NodeNotFoundError):
            repo.get("people/nobody")

    def test_find_returns_none_for_missing(self, repo: Repository) -> None:
        assert repo.find("people/nobody") is None

    def test_walk_ids_skips_proposals(self, repo: Repository) -> None:
        repo.put(person("people/sam-kaur"))
        repo.put_proposal("p-001", person("people/sam-kelly"))
        assert list(repo.walk_ids()) == ["people/sam-kaur"]
        assert list(repo.walk_proposal_ids()) == ["p-001"]

    def test_round_trip_through_store_is_byte_identical(self, repo: Repository) -> None:
        node = person("people/sam-kaur")
        repo.put(node)
        path = Repository.path_for("people/sam-kaur", Sensitivity.INTERNAL)
        first = repo.backend.read_text(path)
        repo.put(repo.get("people/sam-kaur"))
        assert repo.backend.read_text(path) == first

    def test_walk_ids_sorted_across_tiers_not_grouped_by_tier(self, repo: Repository) -> None:
        # Determinism: enumeration order must not depend on which root a node
        # happens to live in, or `cb doctor` reports drift on a reclassification.
        repo.put(person("people/a", Sensitivity.RESTRICTED))
        repo.put(person("people/b", Sensitivity.PUBLIC))
        repo.put(person("people/c", Sensitivity.INTERNAL))
        assert list(repo.walk_ids()) == ["people/a", "people/b", "people/c"]

    def test_walk_ids_filters_by_type_within_every_tier(self, repo: Repository) -> None:
        repo.put(person("people/a", Sensitivity.PUBLIC))
        repo.put(person("people/b", Sensitivity.RESTRICTED))
        assert list(repo.walk_ids("Person")) == ["people/a", "people/b"]
        assert list(repo.walk_ids("Team")) == []

    def test_a_non_node_markdown_file_under_a_tier_root_is_drift(
        self, repo: Repository
    ) -> None:
        repo.backend.write_text("internal/scratch.md", "not a node")
        with pytest.raises(ValueError, match="malformed node id"):
            list(repo.walk_ids())


class TestAclInvariants:
    def test_widening_is_refused(self, repo: Repository) -> None:
        # Invariant 6: a summary of a restricted doc is as restricted as the doc.
        with pytest.raises(AclWideningError, match="may never widen"):
            repo.put(
                person("people/sam-kaur", Sensitivity.PUBLIC),
                input_tiers=(Sensitivity.INTERNAL, Sensitivity.RESTRICTED),
            )

    def test_narrowing_is_allowed(self, repo: Repository) -> None:
        repo.put(
            person("people/sam-kaur", Sensitivity.RESTRICTED),
            input_tiers=(Sensitivity.INTERNAL,),
        )

    def test_matching_tier_is_allowed(self, repo: Repository) -> None:
        repo.put(
            person("people/sam-kaur", Sensitivity.INTERNAL),
            input_tiers=(Sensitivity.INTERNAL, Sensitivity.PUBLIC),
        )

    def test_restricted_node_refused_by_internal_root(self) -> None:
        internal = Repository(MemoryBackend(), tier=Sensitivity.INTERNAL)
        with pytest.raises(TierMismatchError, match="holds internal only"):
            internal.put(person("people/sam-kaur", Sensitivity.RESTRICTED))

    def test_a_refused_write_leaves_nothing_behind(self) -> None:
        # The point of the tier boundary is that the bytes never land, not that
        # they land somewhere and get relabelled.
        backend = MemoryBackend()
        internal = Repository(backend, tier=Sensitivity.INTERNAL)
        with pytest.raises(TierMismatchError):
            internal.put(person("people/sam-kaur", Sensitivity.RESTRICTED))
        assert list(backend.walk()) == []


class TestTierRoots:
    """§6.2: a node's sensitivity picks the physical root it is written into."""

    @pytest.mark.parametrize("tier", list(Sensitivity))
    def test_a_node_is_written_under_its_own_tier_root(
        self, repo: Repository, tier: Sensitivity
    ) -> None:
        repo.put(person("people/sam-kaur", tier))
        assert list(repo.backend.walk()) == [f"{tier_root(tier)}/people/sam-kaur.md"]

    def test_tier_roots_cannot_collide_with_a_type_segment(self) -> None:
        from company_brain.schemas.ids import TYPE_PLURALS

        assert not {tier_root(t) for t in Sensitivity} & set(TYPE_PLURALS.values())

    def test_a_pinned_root_reads_only_its_own_tier(self) -> None:
        backend = MemoryBackend()
        Repository(backend).put(person("people/sam-kaur", Sensitivity.RESTRICTED))
        internal = Repository(backend, tier=Sensitivity.INTERNAL)
        assert internal.find("people/sam-kaur") is None
        assert Repository(backend).find("people/sam-kaur") is not None

    def test_tier_of_reports_the_root_actually_holding_the_node(self, repo: Repository) -> None:
        repo.put(person("people/sam-kaur", Sensitivity.RESTRICTED))
        assert repo.tier_of("people/sam-kaur") is Sensitivity.RESTRICTED
        assert repo.tier_of("people/nobody") is None

    def test_reclassifying_up_removes_the_looser_copy(self, repo: Repository) -> None:
        # The leak this whole layout exists to prevent: a channel goes
        # restricted, and yesterday's copy of its content stays readable in the
        # internal root forever.
        repo.put(person("people/sam-kaur", Sensitivity.INTERNAL))
        repo.put(person("people/sam-kaur", Sensitivity.RESTRICTED))
        assert list(repo.backend.walk()) == ["restricted/people/sam-kaur.md"]
        assert repo.tier_of("people/sam-kaur") is Sensitivity.RESTRICTED

    def test_reclassifying_down_removes_the_stricter_copy(self, repo: Repository) -> None:
        repo.put(person("people/sam-kaur", Sensitivity.RESTRICTED))
        repo.put(person("people/sam-kaur", Sensitivity.PUBLIC))
        assert list(repo.backend.walk()) == ["public/people/sam-kaur.md"]

    def test_a_reclassified_node_is_not_double_counted(self, repo: Repository) -> None:
        repo.put(person("people/sam-kaur", Sensitivity.PUBLIC))
        repo.put(person("people/sam-kaur", Sensitivity.RESTRICTED))
        assert list(repo.walk_ids()) == ["people/sam-kaur"]

    def test_a_duplicate_across_tiers_is_raised_not_silently_picked(
        self, repo: Repository
    ) -> None:
        # Only reachable by an interrupted move or a hand edit, which is exactly
        # why enumeration — what `cb doctor` and the index rebuild both run —
        # must refuse to paper over it.
        repo.put(person("people/sam-kaur", Sensitivity.INTERNAL))
        repo.backend.write_text(
            "public/people/sam-kaur.md",
            repo.backend.read_text("internal/people/sam-kaur.md") or "",
        )
        with pytest.raises(DuplicateNodeError, match="tier move was interrupted"):
            list(repo.walk_ids())

    def test_pinned_roots_skip_the_cross_tier_sweep(self) -> None:
        # A single-tier root can be neither source nor destination of a move, so
        # it must not pay two extra deletes — object-store calls — per write.
        backend = MemoryBackend()
        deletes: list[str] = []
        original = backend.delete

        def counting_delete(path: str) -> bool:
            deletes.append(path)
            return original(path)

        backend.delete = counting_delete  # type: ignore[method-assign]
        Repository(backend, tier=Sensitivity.INTERNAL).put(person("people/sam-kaur"))
        assert deletes == []

    def test_tier_order_runs_least_to_most_restrictive(self) -> None:
        assert TIER_ORDER == (Sensitivity.PUBLIC, Sensitivity.INTERNAL, Sensitivity.RESTRICTED)


class TestTieredBackend:
    """The prod shape: one backend per tier, so the boundary is IAM, not a path."""

    @pytest.fixture
    def parts(self) -> dict[Sensitivity, MemoryBackend]:
        return {t: MemoryBackend() for t in Sensitivity}

    def test_a_node_reaches_only_its_own_tier_backend(
        self, parts: dict[Sensitivity, MemoryBackend]
    ) -> None:
        repo = Repository(TieredBackend(parts))
        repo.put(person("people/sam-kaur", Sensitivity.RESTRICTED))
        assert list(parts[Sensitivity.RESTRICTED].walk()) == ["restricted/people/sam-kaur.md"]
        assert list(parts[Sensitivity.INTERNAL].walk()) == []
        assert list(parts[Sensitivity.PUBLIC].walk()) == []

    def test_keys_match_the_pinned_single_bucket_layout(
        self, parts: dict[Sensitivity, MemoryBackend]
    ) -> None:
        # Promotion from dev to prod has to be a copy, not a rewrite.
        Repository(TieredBackend(parts)).put(person("people/sam-kaur", Sensitivity.RESTRICTED))
        pinned = MemoryBackend()
        Repository(pinned, tier=Sensitivity.RESTRICTED).put(
            person("people/sam-kaur", Sensitivity.RESTRICTED)
        )
        assert list(parts[Sensitivity.RESTRICTED].walk()) == list(pinned.walk())

    def test_round_trip_through_the_router(
        self, parts: dict[Sensitivity, MemoryBackend]
    ) -> None:
        repo = Repository(TieredBackend(parts))
        for tier in Sensitivity:
            repo.put(person(f"people/{tier.value}", tier))
        assert list(repo.walk_ids()) == [
            "people/internal",
            "people/public",
            "people/restricted",
        ]
        assert (
            repo.get("people/restricted").frontmatter.acl.sensitivity is Sensitivity.RESTRICTED
        )

    def test_a_missing_tier_backend_is_refused_at_construction(self) -> None:
        with pytest.raises(ValueError, match="no backend for tier"):
            TieredBackend({Sensitivity.PUBLIC: MemoryBackend()})

    def test_untiered_paths_need_an_explicit_shared_root(
        self, parts: dict[Sensitivity, MemoryBackend]
    ) -> None:
        with pytest.raises(StorePathError, match="outside every tier root"):
            TieredBackend(parts).write_text("_proposals/p-001.md", "x")

    def test_shared_root_takes_the_workflow_trees(
        self, parts: dict[Sensitivity, MemoryBackend]
    ) -> None:
        shared = MemoryBackend()
        repo = Repository(TieredBackend(parts, shared=shared))
        repo.put(person("people/sam-kaur", Sensitivity.PUBLIC))
        repo.put_proposal("p-001", person("people/sam-kelly"))
        assert list(shared.walk()) == ["_proposals/p-001.md"]
        assert list(repo.walk_proposal_ids()) == ["p-001"]
        assert list(repo.walk_ids()) == ["people/sam-kaur"]


class TestTombstonesAndRedirects:
    def test_tombstone_marks_deleted_and_can_drop_the_body(self, repo: Repository) -> None:
        node = Node(frontmatter=person("people/sam-kaur").frontmatter, body="sensitive detail")
        repo.put(node)
        when = datetime(2024, 6, 1, tzinfo=UTC)
        out = repo.tombstone("people/sam-kaur", deleted_at=when, retain_content=False)
        assert out.frontmatter.status is NodeStatus.DELETED
        assert out.frontmatter.deleted_upstream_at == when
        assert "sensitive detail" not in out.body

    def test_tombstone_can_retain_content(self, repo: Repository) -> None:
        node = Node(frontmatter=person("people/sam-kaur").frontmatter, body="why we chose X")
        repo.put(node)
        out = repo.tombstone(
            "people/sam-kaur",
            deleted_at=datetime(2024, 6, 1, tzinfo=UTC),
            retain_content=True,
        )
        assert "why we chose X" in out.body

    def test_redirect_resolves_to_the_live_node(self, repo: Repository) -> None:
        repo.put(person("people/sam-k"))
        repo.put(person("people/sam-kaur"))
        repo.redirect("people/sam-k", "people/sam-kaur")
        # Invariant 12: a citation issued before the merge still resolves.
        assert repo.resolve("people/sam-k").id == "people/sam-kaur"

    def test_redirect_is_reversible_losing_node_survives(self, repo: Repository) -> None:
        repo.put(person("people/sam-k"))
        repo.put(person("people/sam-kaur"))
        repo.redirect("people/sam-k", "people/sam-kaur")
        # §10.1: merges are never destructive, so an unmerge is possible later.
        assert repo.exists("people/sam-k")

    def test_redirect_cycle_detected(self, repo: Repository) -> None:
        repo.put(person("people/a"))
        repo.put(person("people/b"))
        repo.redirect("people/a", "people/b")
        repo.redirect("people/b", "people/a")
        with pytest.raises(StoreError, match="redirect cycle"):
            repo.resolve("people/a")

    def test_self_redirect_refused(self, repo: Repository) -> None:
        repo.put(person("people/a"))
        with pytest.raises(StoreError, match=r"redirect .* to itself"):
            repo.redirect("people/a", "people/a")
