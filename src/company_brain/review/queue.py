"""The review queue.

Three things land here: agent writes (invariant 9), agent-proposed edges, and
extraction output the §11 gates refused to auto-accept. The third is the larger
volume by far — at 201 documents every `owns` edge is already proposed, because
`owns` has no auto-accept threshold at any confidence.

That is the design working, and it is also the design's biggest open cost. Per-
predicate accept-rate is tracked here for exactly that reason: a rate near 100%
means the gate is theatre, and near 10% means the extractor is wasting a
reviewer's time. Neither is visible without measuring it.

Two things this module gained when the agent write path went live:

* **Every decision names a reviewer.** `decide` has no default for it. The
  ROADMAP's demo ends "with the reviewer's name on the provenance", and a queue
  that records *what* was decided but not *by whom* cannot support that sentence
  — nor the M5 audit question, which is the same question asked later.
* **Decisions batch by node.** Fifty accepts against one document used to be
  fifty parse-modify-serialize round trips through the store. The acceptance
  criterion is fifty proposals in fifteen minutes, and a reviewer should not be
  spending any of that budget waiting for the same file to be rewritten fifty
  times.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import StrEnum

from company_brain.audit.log import Action, AuditLog, Outcome
from company_brain.review.proposals import ProposalDiff, ProposalState, ProposalStore
from company_brain.schemas.acl import Principal
from company_brain.schemas.edges import Edge, EdgeStatus
from company_brain.schemas.nodes import Node
from company_brain.store.repository import Repository


class Decision(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


_TARGET: dict[Decision, EdgeStatus] = {
    Decision.ACCEPTED: EdgeStatus.ACCEPTED,
    Decision.REJECTED: EdgeStatus.REJECTED,
    # Reopening is how a misclick is undone. Without it the only correction for
    # a fat-fingered reject is hand-editing markdown, which is exactly the
    # "without opening a terminal" the acceptance criterion rules out.
    Decision.PENDING: EdgeStatus.PROPOSED,
}

_AUDIT_ACTION: dict[Decision, Action] = {
    Decision.ACCEPTED: Action.REVIEW_ACCEPT,
    Decision.REJECTED: Action.REVIEW_REJECT,
    Decision.PENDING: Action.REVIEW_REOPEN,
}


@dataclass(frozen=True, slots=True)
class PendingEdge:
    """One proposed edge awaiting a human."""

    node_id: str
    node_title: str
    edge: Edge

    @property
    def key(self) -> str:
        """Identifies one pending edge. Includes the subject, because two edges
        on the same document can share a predicate and object and differ only
        in who the subject is."""
        return (
            f"{self.node_id}|{self.edge.subject or ''}|{self.edge.predicate}|{self.edge.object}"
        )

    def quote(self) -> str:
        for evidence in self.edge.evidence:
            if evidence.quote:
                return evidence.quote.strip()
        return ""


@dataclass(slots=True)
class QueueStats:
    by_predicate: dict[str, int] = field(default_factory=dict)
    total: int = 0
    with_evidence: int = 0
    proposals: int = 0

    def add(self, item: PendingEdge) -> None:
        key = str(item.edge.predicate)
        self.by_predicate[key] = self.by_predicate.get(key, 0) + 1
        self.total += 1
        if item.edge.evidence:
            self.with_evidence += 1


class ReviewQueue:
    """Edge proposals in the graph, plus agent proposals in ``_proposals/``.

    Both are surfaced from one object because they are one job. An agent write
    path whose output lands somewhere the reviewer's queue does not look is an
    agent write path that only appears to work.
    """

    def __init__(self, repo: Repository, *, audit: AuditLog | None = None) -> None:
        self.repo = repo
        self.audit = audit
        self.proposals = ProposalStore(repo)

    # ---- read ----------------------------------------------------------

    def pending_edges(self, predicate: str | None = None) -> list[PendingEdge]:
        """Every proposed edge in the store, sorted for stable paging."""
        out: list[PendingEdge] = []
        for node in self.repo.walk():
            for edge in node.frontmatter.relations:
                if edge.status is not EdgeStatus.PROPOSED:
                    continue
                if predicate and str(edge.predicate) != predicate:
                    continue
                out.append(PendingEdge(node.id, node.frontmatter.title, edge))
        out.sort(key=lambda p: (str(p.edge.predicate), p.node_id, p.edge.object))
        return out

    def pending_proposals(self, predicate: str | None = None) -> list[ProposalDiff]:
        """Agent proposals awaiting a human, each with its diff computed.

        The diff is computed here rather than on demand because the reviewer's
        first question about a proposal is always "what does it change", and a
        UI that has to ask a second time per item is a UI that costs 18 seconds
        it does not have.
        """
        out: list[ProposalDiff] = []
        for record in self.proposals.records(state=ProposalState.PENDING):
            if predicate and record.predicate != predicate:
                continue
            out.append(self.proposals.diff(record.proposal_id))
        return out

    def kind_of(self, key: str) -> str:
        """``"proposal"`` if a queue row exists under this id, else ``"edge"``.

        For the API the kind is a tag the client carries back, validated on the
        way in. The CLI has no such tag — a human types a key — so it asks the
        queue rather than inferring from the string's shape. "Contains a slash,
        therefore an edge" is the kind of rule that holds until the first
        proposal id that happens to contain one.
        """
        from company_brain.store.repository import PROPOSALS_PREFIX

        if self.repo.backend.exists(f"{PROPOSALS_PREFIX}/{key}.json"):
            return "proposal"
        return "edge"

    def stats(self) -> QueueStats:
        stats = QueueStats()
        for item in self.pending_edges():
            stats.add(item)
        stats.proposals = len(self.proposals.records(state=ProposalState.PENDING))
        return stats

    def accept_rate(self) -> dict[str, tuple[int, int]]:
        """Per-predicate (accepted, decided) counts.

        The number that says whether the gates are calibrated. Reported by
        `cb review stats`; it is the metric ARCHITECTURE §11 asks for and the
        one that decides whether the review burden is sustainable.
        """
        tally: dict[str, list[int]] = {}
        for node in self.repo.walk():
            for edge in node.frontmatter.relations:
                if edge.status not in (EdgeStatus.ACCEPTED, EdgeStatus.REJECTED):
                    continue
                if str(edge.provenance) != "llm":
                    continue  # structural edges bypass the gate; don't flatter the stat
                bucket = tally.setdefault(str(edge.predicate), [0, 0])
                bucket[1] += 1
                if edge.status is EdgeStatus.ACCEPTED:
                    bucket[0] += 1
        return {k: (v[0], v[1]) for k, v in sorted(tally.items())}

    # ---- decide --------------------------------------------------------

    def decide(self, key: str, decision: Decision, *, reviewer: Principal | str) -> Node:
        """Accept, reject, or reopen one proposed edge.

        A rejection is recorded as `status: rejected`, not deleted. Rejected
        proposals are the only signal available for tuning the §11 thresholds —
        throwing them away means never learning that a gate is miscalibrated.

        ``reviewer`` has no default. Invariant 5 makes identity explicit on
        every read path; a write that changes what everyone else sees has no
        weaker claim on the same rule.
        """
        (node,) = self.decide_many([key], decision, reviewer=reviewer)
        return node

    def decide_many(
        self, keys: list[str], decision: Decision, *, reviewer: Principal | str
    ) -> list[Node]:
        """Apply one decision to many edges, one store write per node touched.

        Ordering is the caller's; the writes are grouped by node so a reviewer
        clearing a document's whole backlog pays for one rewrite rather than
        one per edge. A key that does not resolve raises, and nothing is
        written — a partial bulk decision is worse than a refused one, because
        the reviewer cannot tell which half landed.
        """
        target = _TARGET[decision]
        by_node: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
        for key in keys:
            node_id, subject, predicate, obj = key.split("|", 3)
            by_node[node_id].append((subject, predicate, obj))

        # Resolve everything before writing anything.
        planned: list[tuple[Node, list[str]]] = []
        for node_id, wanted in by_node.items():
            node = self.repo.get(node_id)
            updated: list[Edge] = []
            matched: list[str] = []
            outstanding = set(wanted)
            for edge in node.frontmatter.relations:
                signature = (edge.subject or "", str(edge.predicate), edge.object)
                if signature in outstanding:
                    if decision is Decision.PENDING:
                        if edge.status is EdgeStatus.PROPOSED:
                            raise ValueError(f"{node_id} {signature} is already pending")
                    elif edge.status is not EdgeStatus.PROPOSED:
                        raise ValueError(f"{node_id} {signature} is {edge.status}, not pending")
                    updated.append(edge.model_copy(update={"status": target}))
                    matched.append(f"{node_id}|{'|'.join(signature)}")
                    outstanding.discard(signature)
                else:
                    updated.append(edge)
            if outstanding:
                raise KeyError(f"{node_id}: no pending edge for {sorted(outstanding)}")
            planned.append(
                (
                    Node(
                        frontmatter=node.frontmatter.model_copy(
                            update={"relations": tuple(updated)}
                        ),
                        body=node.body,
                    ),
                    matched,
                )
            )

        written: list[Node] = []
        for revised, matched in planned:
            self.repo.put(revised)
            written.append(revised)
            self._record(decision, reviewer, [revised.id], detail=f"{len(matched)} edge(s)")
        return written

    def decide_proposal(
        self, proposal_id: str, decision: Decision, *, reviewer: Principal | str
    ) -> ProposalState:
        """Accept or reject an agent proposal.

        Accepting is the only path from ``_proposals/`` into the graph, and it
        runs under the reviewer's identity: the proposal is the agent's claim,
        the write is the human's decision.
        """
        who = reviewer.id if isinstance(reviewer, Principal) else reviewer
        if decision is Decision.ACCEPTED:
            self.proposals.apply(proposal_id, reviewer=who)
            state = ProposalState.ACCEPTED
            action = Action.PROPOSAL_APPLY
        elif decision is Decision.REJECTED:
            self.proposals.decide(proposal_id, ProposalState.REJECTED, reviewer=who)
            state = ProposalState.REJECTED
            action = Action.PROPOSAL_DISCARD
        else:
            # Undo. Only a rejection is undoable — an acceptance already wrote
            # to the graph, and `reopen` says so rather than pretending.
            self.proposals.reopen(proposal_id, reviewer=who)
            state = ProposalState.PENDING
            action = Action.REVIEW_REOPEN

        record = self.proposals.get_record(proposal_id)
        if self.audit is not None:
            self.audit.record(
                actor=who,
                action=action,
                outcome=Outcome.OK,
                node_ids=[record.target],
                proposal_id=proposal_id,
                detail=f"proposed by {record.proposed_by} for {record.delegated_by}",
            )
        return state

    def _record(
        self,
        decision: Decision,
        reviewer: Principal | str,
        node_ids: list[str],
        *,
        detail: str,
    ) -> None:
        if self.audit is None:
            return
        self.audit.record(
            actor=reviewer,
            action=_AUDIT_ACTION[decision],
            outcome=Outcome.OK,
            node_ids=node_ids,
            detail=detail,
        )
