"""Blocked candidate generation.

Comparing every entity to every other is O(n²) and is the reason naive
resolution stops working somewhere around a few thousand entities. Blocking
replaces it: each entity emits a handful of cheap keys, and only entities that
share a key are ever scored. §10.1 names the three key families — normalized
surname, initials, and email local-part — and this module is those three and
nothing else.

Two properties are load-bearing and both are asserted in tests:

* **Deterministic.** Blocks are sorted, pairs are ordered, and the pair list is
  a sorted tuple. No set iteration reaches the output.
* **Honest about what it dropped.** A key shared by hundreds of entities is not
  a bucket, it is a scan wearing a bucket's clothes: one common surname would
  reintroduce the quadratic cost the whole module exists to avoid. Oversized
  blocks are dropped — and *reported*, never silently, because a silently
  dropped block reads downstream as "we compared them and found nothing".
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from company_brain.resolve.keys import initials_key, parse_email, surname_key
from company_brain.resolve.profiles import EntityProfile

# Above this, a key is not discriminating and its block is dropped. 40 is a
# judgement call: it admits every real surname collision in a mid-size company
# while refusing the pathological keys (a shared inbox aliased by a dozen teams,
# a surname that is also a common word).
DEFAULT_MAX_BLOCK_SIZE = 40


@dataclass(frozen=True, slots=True, order=True)
class BlockKey:
    kind: str
    value: str

    def __str__(self) -> str:
        return f"{self.kind}:{self.value}"


@dataclass(frozen=True, slots=True)
class CandidatePair:
    """Two entities worth scoring, and why they met."""

    left: str  # always the lexicographically smaller ID
    right: str
    keys: tuple[BlockKey, ...]

    @property
    def sort_key(self) -> tuple[str, str]:
        return (self.left, self.right)


@dataclass(frozen=True, slots=True)
class Blocking:
    """The result of a blocking pass, including what it refused to do."""

    pairs: tuple[CandidatePair, ...]
    blocks: tuple[tuple[BlockKey, tuple[str, ...]], ...]
    oversized: tuple[tuple[BlockKey, int], ...]
    entities: int

    @property
    def comparisons(self) -> int:
        return len(self.pairs)

    @property
    def exhaustive_comparisons(self) -> int:
        """What comparing everything to everything would have cost."""
        return self.entities * (self.entities - 1) // 2


def blocking_keys(profile: EntityProfile) -> tuple[BlockKey, ...]:
    """Every block this entity belongs in, sorted and deduplicated.

    Keys come from all of an entity's surface forms, not just its title. The
    duplicate we are hunting is by definition the record whose *title* is the
    unhelpful one — an alias is often the only place the full name survives.
    """
    keys: set[BlockKey] = set()
    for surface in profile.surfaces:
        email = parse_email(surface)
        if email is not None:
            keys.add(BlockKey("email-local", email.local))
            continue
        surname = surname_key(surface)
        if surname is not None:
            keys.add(BlockKey("surname", surname))
        initials = initials_key(surface)
        if initials is not None:
            keys.add(BlockKey("initials", initials))
    return tuple(sorted(keys))


def block(
    profiles: Iterable[EntityProfile], *, max_block_size: int = DEFAULT_MAX_BLOCK_SIZE
) -> Blocking:
    """Bucket entities by key, then emit the within-bucket pairs.

    Entities of different types never pair: "Snowflake" the warehouse and
    "Snowflake" the internal project share every string feature and are not the
    same thing (§10.2). Type is a precondition rather than a scored feature
    because there is no evidence that should ever overturn it.
    """
    materialised = tuple(profiles)
    buckets: dict[BlockKey, list[str]] = {}
    by_id = {profile.node_id: profile for profile in materialised}

    for profile in materialised:
        for key in blocking_keys(profile):
            buckets.setdefault(key, []).append(profile.node_id)

    blocks: list[tuple[BlockKey, tuple[str, ...]]] = []
    oversized: list[tuple[BlockKey, int]] = []
    pair_keys: dict[tuple[str, str], list[BlockKey]] = {}

    for key in sorted(buckets):
        members = tuple(sorted(set(buckets[key])))
        if len(members) < 2:
            continue
        if len(members) > max_block_size:
            oversized.append((key, len(members)))
            continue
        blocks.append((key, members))
        for i, left in enumerate(members):
            for right in members[i + 1 :]:
                if by_id[left].node_type is not by_id[right].node_type:
                    continue
                pair_keys.setdefault((left, right), []).append(key)

    pairs = tuple(
        CandidatePair(left=left, right=right, keys=tuple(sorted(pair_keys[(left, right)])))
        for left, right in sorted(pair_keys)
    )
    return Blocking(
        pairs=pairs,
        blocks=tuple(blocks),
        oversized=tuple(oversized),
        entities=len(materialised),
    )
