"""The store's public API.

Everything upstream of the index goes through here. Two things this layer owns
that a raw backend cannot:

* **ACLs never widen** (invariant 6). Writing a node whose sensitivity is looser
  than its recorded inputs is refused here, at the writer, rather than left to
  each caller's discipline.
* **Tier confinement.** A node lives under the root named for its sensitivity —
  ``restricted/documents/…`` and never ``documents/…`` (docs/ARCHITECTURE.md
  §6.2). A repository pinned to one tier refuses everything else outright. The
  tier is a physical boundary, so the check belongs where the bytes are placed.

This module deliberately has no read-side ACL filtering. The store is not a
permission boundary — enforcement lives in the API/MCP layer, and pretending
otherwise here would give callers false confidence.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from typing import Final

from company_brain.schemas.acl import Sensitivity, narrowest
from company_brain.schemas.edges import Edge, EdgeStatus, Predicate, Provenance
from company_brain.schemas.ids import id_to_path, split_id
from company_brain.schemas.nodes import Frontmatter, Node, NodeStatus
from company_brain.store.backend import StoreBackend, tier_root
from company_brain.store.serialize import dump_node, parse_node

PROPOSALS_PREFIX = "_proposals"
CACHE_PREFIX = "_cache"

# Probe and sweep order: least- to most-restrictive. `find` returning the
# loosest copy of a duplicated ID looks alarming until you follow `_place`: the
# only duplicate it can leave behind is a crashed *widening* move, where the
# loose copy is the newly written one. The strict copy is the stale one.
TIER_ORDER: Final[tuple[Sensitivity, ...]] = (
    Sensitivity.PUBLIC,
    Sensitivity.INTERNAL,
    Sensitivity.RESTRICTED,
)


class StoreError(RuntimeError):
    """A write violated a store invariant."""


class AclWideningError(StoreError):
    """Invariant 6: a derived node may not be more visible than its inputs."""


class TierMismatchError(StoreError):
    """A node's sensitivity does not belong in this store root."""


class NodeNotFoundError(KeyError):
    def __init__(self, node_id: str) -> None:
        super().__init__(node_id)
        self.node_id = node_id


class DuplicateNodeError(StoreError):
    """One node ID exists in more than one tier root."""


class Repository:
    """Read and write canonical nodes over a backend.

    Every node path is ``<tier>/<node_id>.md``. The tier segment is part of the
    path in *both* configurations, so a dev subtree and the production bucket it
    is promoted into hold byte-identical keys, and an ``internal/`` key found
    inside the restricted bucket announces itself as the bug it is.

    ``tier`` pins this repository to one root. Leaving it None gives the
    all-tiers view: writes route by ``acl.sensitivity`` and reads probe. That is
    the dev configuration, and — over a :class:`TieredBackend` — the only
    configuration that can migrate a node whose sensitivity changed upstream,
    since no single bucket can see both sides of that move.

    Production pins a repository per root (separate bucket, separate IAM) so a
    connector bug cannot land restricted content in the internal bucket: it
    raises :class:`TierMismatchError` before the bytes are placed rather than
    writing them somewhere merely mislabelled.
    """

    def __init__(self, backend: StoreBackend, *, tier: Sensitivity | None = None) -> None:
        self.backend = backend
        self.tier = tier

    @property
    def tiers(self) -> tuple[Sensitivity, ...]:
        """Roots this repository may touch, least- to most-restrictive."""
        return (self.tier,) if self.tier is not None else TIER_ORDER

    @staticmethod
    def path_for(node_id: str, tier: Sensitivity) -> str:
        """Store-relative path of a node at a given tier. Validates the ID."""
        return f"{tier_root(tier)}/{id_to_path(node_id)}"

    # ---- read ----------------------------------------------------------

    def get(self, node_id: str) -> Node:
        node = self.find(node_id)
        if node is None:
            raise NodeNotFoundError(node_id)
        return node

    def find(self, node_id: str) -> Node | None:
        for tier in self.tiers:
            text = self.backend.read_text(self.path_for(node_id, tier))
            if text is not None:
                return parse_node(text)
        return None

    def exists(self, node_id: str) -> bool:
        return self.tier_of(node_id) is not None

    def tier_of(self, node_id: str) -> Sensitivity | None:
        """Which root holds this node, or None if no root does.

        Reads the placement rather than the frontmatter on purpose: those two
        disagreeing is exactly the drift `cb doctor` should be able to see.
        """
        for tier in self.tiers:
            if self.backend.exists(self.path_for(node_id, tier)):
                return tier
        return None

    def resolve(self, node_id: str, *, max_hops: int = 8) -> Node:
        """Follow ``redirects_to`` to the live node behind a renamed or merged ID.

        Old citations must always resolve (invariant 12), so this is the read
        path for anything user-facing.
        """
        seen: list[str] = []
        current = node_id
        for _ in range(max_hops):
            if current in seen:
                raise StoreError(f"redirect cycle: {' -> '.join([*seen, current])}")
            seen.append(current)
            node = self.get(current)
            target = node.frontmatter.redirects_to
            if target is None:
                return node
            current = target
        raise StoreError(f"redirect chain longer than {max_hops} hops from {node_id!r}")

    def placements(self, node_type: str | None = None) -> dict[str, Sensitivity]:
        """Every node ID in the store mapped to the root holding it, ID-sorted.

        The workflow trees (``_proposals/``, ``_cache/``, ``_sync/``) sit beside
        the tier roots rather than inside them, so they are excluded here
        structurally instead of by a denylist that a fourth such tree would
        silently fall off.
        """
        suffix = ""
        if node_type is not None:
            from company_brain.schemas.ids import TYPE_PLURALS

            suffix = TYPE_PLURALS[node_type]

        found: dict[str, Sensitivity] = {}
        for tier in self.tiers:
            root = tier_root(tier)
            for path in self.backend.walk(f"{root}/{suffix}" if suffix else root):
                if not path.endswith(".md"):
                    continue
                node_id = path[len(root) + 1 : -len(".md")]
                split_id(node_id)  # a non-node .md under a tier root is drift
                if node_id in found:
                    raise DuplicateNodeError(
                        f"{node_id!r} exists in both {found[node_id]} and {tier}; "
                        "a tier move was interrupted — the stale copy needs removing"
                    )
                found[node_id] = tier
        return dict(sorted(found.items()))

    def walk_ids(self, node_type: str | None = None) -> Iterator[str]:
        """Yield every node ID in the store, sorted, skipping internal trees."""
        yield from self.placements(node_type)

    def walk(self, node_type: str | None = None) -> Iterator[Node]:
        for node_id, tier in self.placements(node_type).items():
            text = self.backend.read_text(self.path_for(node_id, tier))
            if text is not None:
                yield parse_node(text)

    # ---- write ---------------------------------------------------------

    def put(self, node: Node, *, input_tiers: tuple[Sensitivity, ...] = ()) -> None:
        """Write a node, enforcing tier confinement and the no-widening rule.

        ``input_tiers`` is the sensitivity of every source that fed a derived
        node. Supplying it is what makes invariant 6 checkable; a synthesized
        entity page that omits it is trusted, and that trust is the loophole to
        watch in review.
        """
        self._check_tier(node)
        if input_tiers:
            required = narrowest(input_tiers)
            if _looser_than(node.frontmatter.acl.sensitivity, required):
                raise AclWideningError(
                    f"{node.id!r} would be written as "
                    f"{node.frontmatter.acl.sensitivity} but its narrowest input is "
                    f"{required}; extraction may never widen an ACL"
                )
        self._place(node)

    def _place(self, node: Node) -> None:
        """Write the node into its tier root and clear it out of the others.

        There is no atomic rename between roots — in production they are
        different buckets — so the two halves of a tier move are ordered by
        which half-done state we can live with. Looser roots are cleared
        *before* the write and stricter roots *after* it, which means an
        interrupted narrowing leaves the node missing (loud, and the next sync
        rewrites it) and an interrupted widening leaves a duplicate whose stale
        copy is the one in the stricter root (safe, and `placements` raises on
        it). The state we never reach is a stale copy sitting in a root looser
        than the node now belongs to.

        Cost is two extra deletes per write, which is why a pinned repository
        skips the sweep entirely: a single-tier root cannot be the source or the
        destination of a move.
        """
        tier = node.frontmatter.acl.sensitivity
        if self.tier is not None:
            self.backend.write_text(self.path_for(node.id, tier), dump_node(node))
            return

        rank = TIER_ORDER.index(tier)
        for looser in TIER_ORDER[:rank]:
            self.backend.delete(self.path_for(node.id, looser))
        self.backend.write_text(self.path_for(node.id, tier), dump_node(node))
        for stricter in TIER_ORDER[rank + 1 :]:
            self.backend.delete(self.path_for(node.id, stricter))

    def _check_tier(self, node: Node) -> None:
        if self.tier is None:
            return
        actual = node.frontmatter.acl.sensitivity
        if actual is not self.tier:
            raise TierMismatchError(
                f"{node.id!r} is {actual} but this store root holds {self.tier} only"
            )

    def tombstone(
        self,
        node_id: str,
        *,
        deleted_at: datetime,
        retain_content: bool,
        reason: str = "deleted upstream",
    ) -> Node:
        """Mark a node deleted without removing the file (§9.3).

        Inbound edges survive so a citation issued before the delete resolves to
        "this source was deleted on <date>" rather than a dangling ID — a worse
        answer than the tombstone, and a much more confusing one.
        """
        node = self.get(node_id)
        body = node.body if retain_content else f"_{reason} on {deleted_at.date()}._"
        updated = Frontmatter.model_validate(
            node.frontmatter.model_dump()
            | {
                "status": NodeStatus.DELETED,
                "deleted_upstream_at": deleted_at,
                "content_retained": retain_content,
            }
        )
        tombstoned = Node(frontmatter=updated, body=body)
        self.put(tombstoned)
        return tombstoned

    def redirect(self, old_id: str, new_id: str) -> Node:
        """Leave a redirect stub at ``old_id`` pointing to ``new_id``.

        IDs are immutable (invariant 12), so a rename or an entity merge is
        always new-node-plus-stub, never a move. That is also what makes a merge
        reversible: the losing node is still there.
        """
        if old_id == new_id:
            raise StoreError(f"cannot redirect {old_id!r} to itself")
        split_id(new_id)
        existing = self.get(old_id)
        updated = Frontmatter.model_validate(
            existing.frontmatter.model_dump()
            | {
                "status": NodeStatus.MERGED,
                "redirects_to": new_id,
                "relations": [
                    *(
                        e.model_dump()
                        for e in existing.frontmatter.relations
                        if e.predicate is not Predicate.REDIRECTS_TO
                    ),
                    Edge(
                        predicate=Predicate.REDIRECTS_TO,
                        object=new_id,
                        confidence=1.0,
                        provenance=Provenance.HUMAN,
                        status=EdgeStatus.ACCEPTED,
                    ).model_dump(),
                ],
            }
        )
        stub = Node(frontmatter=updated, body=f"Merged into [[{new_id}]].")
        self.put(stub)
        return stub

    # ---- proposals -----------------------------------------------------

    def put_proposal(self, proposal_id: str, node: Node) -> str:
        """Write an agent or low-confidence write to the proposal tree.

        Agents never mutate the graph (invariant 9). Proposals are real markdown
        so a reviewer diffs them in the same editor as everything else.

        Unlike nodes, proposals are **not** tier-partitioned yet, so a proposal
        derived from a restricted node lands in a root shared with every other
        tier. Same gap as ``_cache/extraction/``; see ARCHITECTURE §6.2.
        """
        path = f"{PROPOSALS_PREFIX}/{proposal_id}.md"
        self.backend.write_text(path, dump_node(node))
        return path

    def walk_proposal_ids(self) -> Iterator[str]:
        for path in self.backend.walk(PROPOSALS_PREFIX):
            if path.endswith(".md"):
                yield path[len(PROPOSALS_PREFIX) + 1 : -len(".md")]


_TIER_RANK = {Sensitivity.PUBLIC: 0, Sensitivity.INTERNAL: 1, Sensitivity.RESTRICTED: 2}


def _looser_than(candidate: Sensitivity, floor: Sensitivity) -> bool:
    return _TIER_RANK[candidate] < _TIER_RANK[floor]
