"""Layer 3, assembled: profile -> block -> score -> propose.

The four layers of §10.1 are cheapest-and-most-certain first, and this module is
only the third. Layers 1 and 2 — identity keys from source systems, and curated
aliases on entity pages — already exist elsewhere: connectors write the keys,
humans write the aliases, and both arrive here as an entity's surface forms.
Layer 4 is the absence of a decision: an unresolved mention stays
``mentions_unresolved`` and is never guessed into an existing person, which is
the extractor's job and not this module's.

What layer 3 adds is the only part that is allowed to be wrong: a scored guess
about two records that *might* be one. So it ends in a proposal, every time.

**Process and Decision are deliberately not resolved here.** §10.3 is
unambiguous that their names are invented by the extractor, so string similarity
over them measures the model's phrasing variance and co-occurrence measures
which documents the model happened to name them in. The section asks for
embedding-plus-participant clustering presented to a human who names the process
once — a different algorithm with a different UI, and one that needs the
embedder from `index/`. `run()` counts them and reports the count rather than
quietly leaving them out.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from company_brain.resolve.blocking import (
    DEFAULT_MAX_BLOCK_SIZE,
    Blocking,
    CandidatePair,
    block,
)
from company_brain.resolve.keys import identity_conflict, identity_surface
from company_brain.resolve.profiles import EntityProfile, build_profiles
from company_brain.resolve.proposals import SameAsProposal, build_edge
from company_brain.resolve.scoring import Policy, ScoreCard, Weights, score_pair
from company_brain.schemas.edges import Evidence
from company_brain.schemas.nodes import NodeType
from company_brain.store.repository import Repository

# Enough for a reviewer to check the claim; not so much that the frontmatter
# becomes unreadable. Capped rather than unbounded because a popular entity
# co-occurs with its duplicate in hundreds of documents and listing all of them
# turns evidence into noise.
MAX_DOCUMENT_EVIDENCE = 3
MAX_KEY_EVIDENCE = 2

# Types §10.3 says must not be resolved by string and co-occurrence features.
DEFERRED_TYPES: tuple[NodeType, ...] = (NodeType.PROCESS, NodeType.DECISION)


@dataclass(frozen=True, slots=True)
class ResolutionReport:
    """Everything one layer-3 pass decided, including what it declined to do."""

    proposals: tuple[SameAsProposal, ...]
    considered: tuple[ScoreCard, ...]
    blocking: Blocking
    deferred: tuple[tuple[str, int], ...]

    @property
    def vetoed(self) -> tuple[ScoreCard, ...]:
        return tuple(card for card in self.considered if card.veto is not None)

    def summary(self) -> str:
        """One human-readable paragraph. Reports the caps, never hides them."""
        lines = [
            f"entities profiled: {self.blocking.entities}",
            f"blocks: {len(self.blocking.blocks)}",
            f"pairs compared: {self.blocking.comparisons}"
            f" (all-pairs would be {self.blocking.exhaustive_comparisons})",
            f"vetoed: {len(self.vetoed)}",
            f"proposals: {len(self.proposals)}",
        ]
        for key, size in self.blocking.oversized:
            lines.append(f"block {key} dropped: {size} members, above the cap — NOT compared")
        for type_name, count in self.deferred:
            lines.append(f"{type_name}: {count} nodes deferred, see §10.3")
        return "\n".join(lines)


class Layer3Resolver:
    """Blocked candidate generation plus scored matching, ending in proposals."""

    def __init__(
        self,
        repo: Repository,
        *,
        weights: Weights | None = None,
        policy: Policy | None = None,
        max_block_size: int = DEFAULT_MAX_BLOCK_SIZE,
    ) -> None:
        self.repo = repo
        self.weights = weights or Weights()
        self.policy = policy or Policy()
        self.max_block_size = max_block_size

    def run(self) -> ResolutionReport:
        profiles = build_profiles(self.repo)
        by_id = {profile.node_id: profile for profile in profiles}
        blocking = block(profiles, max_block_size=self.max_block_size)

        considered: list[ScoreCard] = []
        proposals: list[SameAsProposal] = []
        for pair in blocking.pairs:
            left, right = by_id[pair.left], by_id[pair.right]
            card = score_pair(
                left,
                right,
                weights=self.weights,
                policy=self.policy,
                veto=identity_conflict(left.surfaces, right.surfaces),
            )
            considered.append(card)
            if card.veto is not None or card.score < self.policy.propose_above:
                continue
            proposals.append(self._propose(left, right, card, pair))

        # Highest score first so a reviewer meets the strongest claims while
        # they still have patience; ties broken by ID, never by insertion order.
        proposals.sort(key=lambda p: (-p.score, p.winner, p.loser))
        return ResolutionReport(
            proposals=tuple(proposals),
            considered=tuple(considered),
            blocking=blocking,
            deferred=self._deferred(),
        )

    def _deferred(self) -> tuple[tuple[str, int], ...]:
        return tuple(
            (str(node_type), sum(1 for _ in self.repo.walk_ids(str(node_type))))
            for node_type in DEFERRED_TYPES
        )

    def _propose(
        self,
        left: EntityProfile,
        right: EntityProfile,
        card: ScoreCard,
        pair: CandidatePair,
    ) -> SameAsProposal:
        winner, loser = _canonical_side(left, right)
        evidence = self._evidence(winner, loser)
        return SameAsProposal(
            winner=winner.node_id,
            loser=loser.node_id,
            card=card,
            keys=pair.keys,
            edge=build_edge(loser.node_id, card, evidence),
        )

    def _evidence(self, winner: EntityProfile, loser: EntityProfile) -> tuple[Evidence, ...]:
        """What a reviewer can check, in the order they would check it.

        Identity keys first — a shared corporate address settles most real
        cases in one glance. Then the documents where both records appear, with
        a *computed* span into the stored body, not a remembered one: the same
        rule `extract/claude.py` follows, because an offset that lands on the
        wrong sentence is worse than no offset at all.
        """
        out: list[Evidence] = []
        shared_keys = sorted(set(winner.identity_keys) & set(loser.identity_keys))
        for key in shared_keys[:MAX_KEY_EVIDENCE]:
            # Quote the address the losing node actually carries, not the
            # normalized match key (`keys.identity_surface`).
            out.append(
                Evidence(node=loser.node_id, quote=identity_surface(loser.surfaces, key))
            )

        shared_docs = sorted(set(winner.mentioned_in) & set(loser.mentioned_in))
        for document_id in shared_docs[:MAX_DOCUMENT_EVIDENCE]:
            located = self._locate(document_id, loser)
            if located is not None:
                out.append(located)

        if not out:
            # An LLM-provenance edge with no evidence cannot be reviewed and is
            # rejected at construction (`Edge._llm_edges_cite`). The surface
            # form that matched is the minimum honest citation.
            out.append(Evidence(node=loser.node_id, quote=loser.title))
        return tuple(out)

    def _locate(self, document_id: str, profile: EntityProfile) -> Evidence | None:
        """Find one of this entity's surface forms in a document body."""
        node = self.repo.find(document_id)
        if node is None:
            return None
        body = node.body
        lowered = body.lower()
        # Longest surface first: "Sam Kaur" is better evidence than "Sam".
        for surface in sorted(set(profile.surfaces), key=lambda s: (-len(s), s)):
            match = re.search(rf"(?<!\w){re.escape(surface.lower())}(?!\w)", lowered)
            if match is None:
                continue
            span = (match.start(), match.end())
            return Evidence(node=document_id, span=span, quote=body[span[0] : span[1]])
        return None


def _canonical_side(
    left: EntityProfile, right: EntityProfile
) -> tuple[EntityProfile, EntityProfile]:
    """Which record survives.

    The one the graph has more to say about, because merging the well-cited
    record into the sparse one would leave every existing citation pointing at a
    tombstone. Ties go to the lexicographically smaller ID so the choice is
    stable across runs rather than dependent on iteration order.
    """
    ranked = sorted((left, right), key=lambda p: (-p.evidence_weight, p.node_id))
    return ranked[0], ranked[1]
