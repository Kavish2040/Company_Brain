"""Reversible merges, and the review workflow that drives them.

ROADMAP M3 asks for one thing above all others here: *a merge, then an unmerge,
then a re-ingest returns the store to a byte-identical state.* That sentence
rules out the natural implementation.

`Repository.redirect` is the store's existing rename path and it is right for a
rename: the old ID becomes a stub whose body reads "Merged into [[x]]", because
after a rename there is no old content to keep. A merge is not a rename. The
losing node is a real record with real prose, §10.1 says a merge "never
destroys the losing node", and a merge that overwrites its body is unmergeable
in practice — `LocalIngest._write_entities` skips nodes that already exist
(invariant 13), so no later ingest will put the prose back either.

So a merge here is two edits chosen to be exactly invertible:

* the **losing** node gains ``status: merged``, ``redirects_to``, and one
  ``redirects_to`` edge. Its body, aliases, timestamps and every other relation
  are untouched.
* the **winning** node gains exactly one ``same_as`` edge.

Unmerge removes precisely those, identified by target rather than by position,
so a pre-existing ``same_as`` or ``redirects_to`` edge pointing somewhere else
survives. Everything that could make the pair non-invertible is refused up front
instead of being handled halfway through.

What this module does *not* do is decide anything. It is driven by a human
accepting a proposal; `resolve/` never calls `merge` on its own.
"""

from __future__ import annotations

from dataclasses import dataclass

from company_brain.resolve.proposals import SameAsProposalStore
from company_brain.review.queue import Decision
from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance
from company_brain.schemas.nodes import Frontmatter, Node, NodeStatus
from company_brain.store.repository import NodeNotFoundError, Repository


class MergeError(RuntimeError):
    """A merge or unmerge would not be reversible, so it was refused."""


@dataclass(frozen=True, slots=True)
class MergeRecord:
    """What a merge did.

    ``decided_by`` is carried here and written into the proposal's decision
    fence, because no edge field can hold it: `Provenance` has three values and
    none of them is a person. ROADMAP M3's demo wants "the reviewer's name on
    the provenance" — that needs a schema change this work does not own. See the
    flags in `resolve/__init__.py`.
    """

    winner: str
    loser: str
    decided_by: str


class Merger:
    """Applies and reverses entity merges. Human-decided; never automatic."""

    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def merge(
        self,
        winner_id: str,
        loser_id: str,
        *,
        decided_by: str,
        evidence: tuple[Evidence, ...] = (),
    ) -> MergeRecord:
        winner, loser = self._pair(winner_id, loser_id)

        if winner.type is not loser.type:
            raise MergeError(
                f"cannot merge {loser_id!r} into {winner_id!r}: "
                f"type {loser.type} is not {winner.type}"
            )
        # Specific causes before the general one. A merged node is also inactive,
        # and "is merged, not active" sends a reader looking for a status bug
        # instead of telling them the pair is already resolved.
        if _same_as_edge(winner, loser_id) is not None:
            raise MergeError(f"{winner_id!r} is already merged with {loser_id!r}")
        if loser.frontmatter.redirects_to is not None:
            raise MergeError(
                f"{loser_id!r} already redirects to {loser.frontmatter.redirects_to!r}"
            )
        for node in (winner, loser):
            if node.frontmatter.status is not NodeStatus.ACTIVE:
                raise MergeError(f"{node.id!r} is {node.frontmatter.status}, not active")

        # Winner first. The two writes are individually atomic but not atomic
        # together (invariant 14 is per file), so the intermediate state is
        # chosen to be the harmless one: a `same_as` edge to a node that is
        # still active reads as a recorded duplicate, whereas a tombstone with
        # no surviving edge loses the reason the redirect exists.
        self.repo.put(_add_same_as(winner, loser_id, evidence))
        self.repo.put(_tombstone_into(loser, winner_id))
        return MergeRecord(winner=winner_id, loser=loser_id, decided_by=decided_by)

    def unmerge(self, winner_id: str, loser_id: str) -> MergeRecord:
        """Restore both nodes to their pre-merge bytes.

        The losing node's tombstone is required; the winner's ``same_as`` edge
        is not, so a half-applied merge can still be cleaned up rather than
        becoming permanent because the repair path was fussier than the damage.
        """
        winner, loser = self._pair(winner_id, loser_id)

        if (
            loser.frontmatter.status is not NodeStatus.MERGED
            or loser.frontmatter.redirects_to != winner_id
        ):
            raise MergeError(f"{loser_id!r} is not merged into {winner_id!r}")

        self.repo.put(_restore(loser, winner_id))
        if _same_as_edge(winner, loser_id) is not None:
            self.repo.put(_drop_same_as(winner, loser_id))
        return MergeRecord(winner=winner_id, loser=loser_id, decided_by="")

    def merged_into(self, winner_id: str) -> tuple[str, ...]:
        """Every node currently merged into this one, sorted."""
        winner = self._require(winner_id)
        return tuple(
            sorted(
                edge.object
                for edge in winner.frontmatter.relations
                if edge.predicate is Predicate.SAME_AS and edge.status is EdgeStatus.ACCEPTED
            )
        )

    def _pair(self, winner_id: str, loser_id: str) -> tuple[Node, Node]:
        if winner_id == loser_id:
            raise MergeError(f"cannot merge {winner_id!r} into itself")
        return self._require(winner_id), self._require(loser_id)

    def _require(self, node_id: str) -> Node:
        try:
            return self.repo.get(node_id)
        except NodeNotFoundError as exc:
            raise MergeError(f"{node_id!r} is not in the store") from exc


class ReviewWorkflow:
    """Accept, reject, and revert `same_as` proposals.

    Every path is invertible by `revert`, including a rejection — a reviewer who
    rejects the wrong proposal should not have to hand-edit markdown to undo it.
    """

    def __init__(self, repo: Repository) -> None:
        self.repo = repo
        self.proposals = SameAsProposalStore(repo)
        self.merger = Merger(repo)

    def accept(self, proposal_id: str, *, decided_by: str) -> MergeRecord:
        node = self.proposals.read(proposal_id)
        edge = self.proposals.edge_of(proposal_id)
        record = self.merger.merge(
            node.id, edge.object, decided_by=decided_by, evidence=edge.evidence
        )
        self.proposals.decide(proposal_id, Decision.ACCEPTED, decided_by=decided_by)
        return record

    def reject(self, proposal_id: str, *, decided_by: str) -> None:
        """Record a rejection. The graph is not touched — that is the point."""
        self.proposals.decide(proposal_id, Decision.REJECTED, decided_by=decided_by)

    def revert(self, proposal_id: str) -> MergeRecord | None:
        """Undo a decision, whichever way it went."""
        node = self.proposals.read(proposal_id)
        edge = self.proposals.edge_of(proposal_id)
        record = None
        if edge.status is EdgeStatus.ACCEPTED:
            record = self.merger.unmerge(node.id, edge.object)
        self.proposals.reopen(proposal_id)
        return record


# ---- the four edits, each the inverse of one other ----------------------


def _same_as_edge(node: Node, target: str) -> Edge | None:
    return next(
        (
            edge
            for edge in node.frontmatter.relations
            if edge.predicate is Predicate.SAME_AS and edge.object == target
        ),
        None,
    )


def _revalidate(node: Node, changes: dict[str, object], body: str) -> Node:
    """Rebuild a frontmatter through validation rather than `model_copy`.

    `model_copy(update=...)` skips validators, so a merge built that way could
    write a node the parser would later reject. Round-tripping through
    `model_validate` is what `Repository.tombstone` and `redirect` already do.
    """
    return Node(
        frontmatter=Frontmatter.model_validate(node.frontmatter.model_dump() | changes),
        body=body,
    )


def _add_same_as(winner: Node, loser_id: str, evidence: tuple[Evidence, ...]) -> Node:
    edge = Edge(
        predicate=Predicate.SAME_AS,
        object=loser_id,
        confidence=1.0,
        # A human decided this, so it is not the LLM-scored proposal any more.
        provenance=Provenance.HUMAN,
        status=EdgeStatus.ACCEPTED,
        evidence=evidence,
    )
    return _revalidate(
        winner,
        {
            "relations": [
                *(e.model_dump() for e in winner.frontmatter.relations),
                edge.model_dump(),
            ]
        },
        winner.body,
    )


def _drop_same_as(winner: Node, loser_id: str) -> Node:
    return _revalidate(
        winner,
        {
            "relations": [
                e.model_dump()
                for e in winner.frontmatter.relations
                if not (e.predicate is Predicate.SAME_AS and e.object == loser_id)
            ]
        },
        winner.body,
    )


def _tombstone_into(loser: Node, winner_id: str) -> Node:
    redirect = Edge(
        predicate=Predicate.REDIRECTS_TO,
        object=winner_id,
        confidence=1.0,
        provenance=Provenance.HUMAN,
        status=EdgeStatus.ACCEPTED,
    )
    return _revalidate(
        loser,
        {
            "status": NodeStatus.MERGED,
            "redirects_to": winner_id,
            "relations": [
                *(e.model_dump() for e in loser.frontmatter.relations),
                redirect.model_dump(),
            ],
        },
        # The whole point: the losing node keeps its content (§10.1).
        loser.body,
    )


def _restore(loser: Node, winner_id: str) -> Node:
    return _revalidate(
        loser,
        {
            "status": NodeStatus.ACTIVE,
            "redirects_to": None,
            "relations": [
                e.model_dump()
                for e in loser.frontmatter.relations
                # Only the edge this merge added. A redirect pointing elsewhere
                # predates the merge and is not ours to remove.
                if not (e.predicate is Predicate.REDIRECTS_TO and e.object == winner_id)
            ],
        },
        loser.body,
    )
