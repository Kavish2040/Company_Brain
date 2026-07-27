"""`same_as` proposals: shaped, written, and decided.

Layer 3 never merges anything. It writes a proposal into ``store/_proposals/``
and stops — the same rule invariant 9 puts on agents, for the same reason: an
automated writer that can act on its own inference has no failure mode a human
can catch in time. §10.1 is explicit that layer 3 proposes and never
auto-merges, and §10.2 is explicit that Person never auto-merges at all.

A proposal file is shaped exactly like `McpTools.propose_edge` shapes one: the
node as it *would* look if accepted, so a reviewer reads a diff rather than a
report. The scoring breakdown that justifies it lives in a generated fence
(`store/fences.py`), which is the repo's existing answer to "machine-written
text inside a file a human also owns" — and it keeps the rationale out of the
index, since `strip_regions` already removes it during chunking.

Deciding a proposal is reversible on both sides. Accepting stamps the file and
merges; reverting unstamps it and unmerges, byte for byte. That symmetry is
what ROADMAP M3's byte-identity criterion is really testing, and it is why the
decision stamp is its own region rather than an edit to the rationale: removing
a whole region restores the previous bytes exactly, whereas rewriting prose
back into a prior state is a guess.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from company_brain.resolve.blocking import BlockKey
from company_brain.resolve.scoring import ScoreCard
from company_brain.review.queue import Decision, PendingEdge
from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance
from company_brain.schemas.nodes import Node
from company_brain.store.fences import find_regions, render_fence, upsert_region
from company_brain.store.repository import PROPOSALS_PREFIX, Repository
from company_brain.store.serialize import parse_node

PROPOSAL_PREFIX: Final = "same-as"
RATIONALE_REGION: Final = "resolve-rationale"
DECISION_REGION: Final = "resolve-decision"


class SameAsProposalError(RuntimeError):
    """A proposal file is missing, malformed, or in the wrong state."""


@dataclass(frozen=True, slots=True)
class SameAsProposal:
    """One `winner --same_as--> loser` claim, with everything behind it.

    ``winner`` is the record that survives a merge. It is chosen by evidence
    weight — how many documents point at each side — and not by which record
    looks tidier, because the tidy record is frequently the freshly created
    duplicate.
    """

    winner: str
    loser: str
    card: ScoreCard
    keys: tuple[BlockKey, ...]
    edge: Edge

    @property
    def proposal_id(self) -> str:
        return f"{PROPOSAL_PREFIX}-{_flatten(self.winner)}-{_flatten(self.loser)}"

    @property
    def score(self) -> float:
        return self.card.score

    def rationale(self) -> str:
        """The fenced block a reviewer reads before deciding."""
        blocked_on = ", ".join(str(key) for key in self.keys) or "n/a"
        lines = [
            f"Proposed merge: **{self.loser}** into **{self.winner}**.",
            "",
            f"Blocked on: `{blocked_on}`",
            "",
            self.card.table(),
            "",
            "Accepting writes a `same_as` edge and a redirect tombstone; the losing",
            "node keeps its content and the merge can be reverted (§10.1).",
        ]
        return "\n".join(lines)


def _flatten(node_id: str) -> str:
    return node_id.replace("/", "-")


def build_edge(loser: str, card: ScoreCard, evidence: tuple[Evidence, ...]) -> Edge:
    """The proposed edge, with its status decided by the §11 gate table.

    Routed through `decide_status` rather than hardcoded to PROPOSED so there is
    one implementation of the gate policy — and then checked, because if someone
    ever gives `same_as` an auto-accept threshold, layer 3 must fail loudly
    rather than quietly start merging people.
    """
    from company_brain.schemas.edges import decide_status

    status = decide_status(Predicate.SAME_AS, card.score, Provenance.LLM, evidence)
    if status is not EdgeStatus.PROPOSED:
        raise SameAsProposalError(
            f"the gate table would have auto-accepted a same_as edge to {loser!r}; "
            "§10.2 forbids auto-merging an entity on inference alone"
        )
    return Edge(
        predicate=Predicate.SAME_AS,
        object=loser,
        confidence=round(card.score, 4),
        provenance=Provenance.LLM,
        status=status,
        evidence=evidence,
    )


class SameAsProposalStore:
    """Reads and writes the `same_as` proposals under ``store/_proposals/``."""

    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    # ---- write ---------------------------------------------------------

    def write(self, proposal: SameAsProposal) -> str:
        """Persist one proposal. Returns its ID.

        The graph is not touched. The winner node is read, given the proposed
        edge and the rationale fence, and written to the proposal tree — the
        original file on the graph side is never opened for writing.
        """
        winner = self.repo.find(proposal.winner)
        if winner is None:
            raise SameAsProposalError(f"winner {proposal.winner!r} is not in the store")
        merged = _with_edge(winner, proposal.edge)
        body = upsert_region(winner.body, RATIONALE_REGION, proposal.rationale())
        self.repo.put_proposal(
            proposal.proposal_id, Node(frontmatter=merged.frontmatter, body=body)
        )
        return proposal.proposal_id

    def write_all(self, proposals: tuple[SameAsProposal, ...]) -> tuple[str, ...]:
        return tuple(self.write(p) for p in proposals)

    # ---- read ----------------------------------------------------------

    def proposal_ids(self) -> list[str]:
        return sorted(
            pid
            for pid in self.repo.walk_proposal_ids()
            if pid.startswith(f"{PROPOSAL_PREFIX}-")
        )

    def read(self, proposal_id: str) -> Node:
        """Load one proposal file.

        `Repository` has `put_proposal` and `walk_proposal_ids` but no reader,
        so this reaches the backend directly. It uses the repository's own
        `PROPOSALS_PREFIX` rather than a second copy of the path convention —
        the proposal tree is not tier-partitioned, unlike the graph, so
        `Repository.path_for` is the wrong helper here.
        """
        text = self.repo.backend.read_text(f"{PROPOSALS_PREFIX}/{proposal_id}.md")
        if text is None:
            raise SameAsProposalError(f"no proposal {proposal_id!r}")
        return parse_node(text)

    def edge_of(self, proposal_id: str) -> Edge:
        """The one `same_as` edge a proposal file carries."""
        node = self.read(proposal_id)
        edges = [e for e in node.frontmatter.relations if e.predicate is Predicate.SAME_AS]
        if len(edges) != 1:
            raise SameAsProposalError(
                f"{proposal_id!r} carries {len(edges)} same_as edges; expected exactly 1"
            )
        return edges[0]

    def pending(self) -> list[PendingEdge]:
        """Undecided proposals, in the shape `review.queue` already speaks.

        `ReviewQueue.pending_edges` walks the *graph*, and `Repository.walk`
        skips ``_proposals/`` by design, so these are invisible to it today.
        Returning its `PendingEdge` type means the CLI and the review UI need no
        second vocabulary once the queue learns to read this tree — see the
        wiring note in `resolve/__init__.py`.
        """
        out: list[PendingEdge] = []
        for proposal_id in self.proposal_ids():
            node = self.read(proposal_id)
            for edge in node.frontmatter.relations:
                if edge.predicate is Predicate.SAME_AS and edge.status is EdgeStatus.PROPOSED:
                    out.append(PendingEdge(node.id, node.frontmatter.title, edge))
        out.sort(key=lambda p: (p.node_id, p.edge.object))
        return out

    # ---- decide --------------------------------------------------------

    def decide(self, proposal_id: str, decision: Decision, *, decided_by: str) -> Node:
        """Stamp a proposal accepted or rejected.

        Mirrors `ReviewQueue.decide`: a rejection is recorded, never deleted,
        because rejections are the only signal available for telling a
        miscalibrated threshold from a working one.
        """
        node = self.read(proposal_id)
        edge = self.edge_of(proposal_id)
        if edge.status is not EdgeStatus.PROPOSED:
            raise SameAsProposalError(f"{proposal_id!r} is {edge.status}, not pending")

        target = EdgeStatus.ACCEPTED if decision is Decision.ACCEPTED else EdgeStatus.REJECTED
        stamped = _with_edge(node, edge.model_copy(update={"status": target}))
        body = upsert_region(node.body, DECISION_REGION, f"{decision.value} by {decided_by}")
        revised = Node(frontmatter=stamped.frontmatter, body=body)
        self.repo.put_proposal(proposal_id, revised)
        return revised

    def reopen(self, proposal_id: str) -> Node:
        """Undo a decision, restoring the file to its pre-decision bytes."""
        node = self.read(proposal_id)
        edge = self.edge_of(proposal_id)
        if edge.status is EdgeStatus.PROPOSED:
            raise SameAsProposalError(f"{proposal_id!r} is already pending")

        reopened = _with_edge(node, edge.model_copy(update={"status": EdgeStatus.PROPOSED}))
        revised = Node(
            frontmatter=reopened.frontmatter, body=remove_region(node.body, DECISION_REGION)
        )
        self.repo.put_proposal(proposal_id, revised)
        return revised


def remove_region(body: str, name: str) -> str:
    """Delete a fenced region, restoring the bytes `upsert_region` appended.

    `store/fences.py` can add and replace a region but not remove one, so the
    inverse lives here rather than as an edit to a module this work does not
    own. It is the exact inverse of an append: cut the fence, then drop the
    blank-line separator that the append introduced.
    """
    region = next((r for r in find_regions(body) if r.name == name), None)
    if region is None:
        return body
    before = body[: region.start].rstrip("\n")
    after = body[region.end :].lstrip("\n")
    if before and after:
        return f"{before}\n\n{after}"
    return before or after


def _with_edge(node: Node, edge: Edge) -> Node:
    keyed = {e.sort_key(): e for e in node.frontmatter.relations}
    keyed[edge.sort_key()] = edge
    return Node(
        frontmatter=node.frontmatter.model_copy(update={"relations": tuple(keyed.values())}),
        body=node.body,
    )


def render_rationale_fence(content: str) -> str:
    """Exposed for tests that need the exact bytes a rationale fence produces."""
    return render_fence(RATIONALE_REGION, content)
