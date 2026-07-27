"""The wall between an agent and the graph.

Invariant 9 says agents never write to the graph. Until now that held by
*absence*: no MCP tool called ``Repository.put``, so nothing could. Absence is a
real defence and a bad one to rely on — it cannot be tested except by grepping
for what isn't there, it produces no audit trail when someone tries, and it
degrades the moment a sixth tool is added by someone who has not read this file.

So the store the agent surface holds is not a ``Repository``. It is this: reads
that are ACL-checked before they return bytes, one write that produces a
proposal, and the mutating half of the repository API present but refusing —
because a refusal that can be *called* is a refusal that can be tested and
audited, and "an agent attempting a direct graph write is rejected; the attempt
is audited" (ROADMAP M3) is not a claim you can make about an AttributeError.

Three refusals live here, and the distinction between them is deliberate:

* :class:`AgentWriteRefused` — you asked to mutate the graph. Nothing can.
* :class:`AclWideningBlocked` — invariant 6 and §11's last row. A **block**, not
  a proposal: queueing it would mean a reviewer could accept it, and the whole
  point is that no human decision can make this safe.
* :class:`PatchFieldRefused` — you tried to patch a field that is not yours to
  patch. Refused loudly rather than dropped silently, because an agent whose
  ACL edit is quietly ignored believes it succeeded.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, NoReturn

from company_brain.audit.log import Action, AuditLog, Outcome
from company_brain.collab.guard import FenceViolation, check_generated_regions
from company_brain.review.proposals import (
    ProposalRecord,
    ProposalStore,
    content_sha256,
)
from company_brain.schemas.acl import Principal, Sensitivity, at_least, narrowest
from company_brain.schemas.nodes import Node
from company_brain.store.serialize import dump_node

if TYPE_CHECKING:
    from company_brain.acl.grants import AccessFilter
    from company_brain.index.memory import MemoryIndex
    from company_brain.store.repository import Repository

# Frontmatter an agent proposal may change. Everything else — `acl`, `id`,
# `type`, `status`, `source`, `extraction` — is either identity, provenance, or
# permission, and none of the three is an agent's to restate.
#
# `aliases` is here because curated aliases are §10.1's layer 2, and "this
# person also signs as @samk" is exactly the observation an agent reading four
# threads is well placed to make and a human is well placed to check.
PATCHABLE: Final[frozenset[str]] = frozenset({"body", "aliases"})

# Naming the ACL fields separately so the refusal can say *why* rather than
# "unknown field", and so the audit record classifies it as a widening attempt.
ACL_FIELDS: Final[frozenset[str]] = frozenset({"acl", "sensitivity", "acl_ref"})


class AgentWriteRefused(PermissionError):
    """An agent attempted a direct graph mutation."""


class AclWideningBlocked(PermissionError):
    """A write would have made something visible to more people than its inputs.

    Blocked, never queued. ARCHITECTURE §11's table ends with "anything that
    would widen an ACL → hard block, not a proposal", and a queued widening is
    a widening with a human's name attached to it.
    """


class PatchFieldRefused(PermissionError):
    """A patch named a field outside the agent-writable set."""


class NotVisible(KeyError):
    """The node does not exist, or the session may not see it.

    One exception for both, deliberately (§6.3): distinguishing them turns
    ``read_node`` into an existence oracle for content the caller cannot read.
    """


class ProposalOnlyStore:
    """Everything an agent may do to the store. The rest is a wall.

    Constructed per session, holding that session's principal and access filter,
    so no method takes an identity — there is no argument a model can pass to
    become somebody else (invariant 8).
    """

    def __init__(
        self,
        repo: Repository,
        *,
        index: MemoryIndex,
        access: AccessFilter,
        principal: Principal,
        audit: AuditLog,
        proposals: ProposalStore | None = None,
        may_propose: bool = True,
    ) -> None:
        self._repo = repo
        self._index = index
        self._access = access
        self._principal = principal
        self._audit = audit
        self._proposals = proposals if proposals is not None else ProposalStore(repo)
        self.may_propose = may_propose

    # ---- reads, ACL-checked --------------------------------------------

    def visible(self, node_id: str) -> Node:
        """The stored node, if this session may see it. Raises otherwise.

        The check runs against the index — the same ``allows`` call every other
        surface makes (invariant 5a) — and only then reads the file. Reading
        first and filtering after is how a leak gets written into a log line.
        """
        indexed = self._index.get_node(node_id)
        if indexed is None or not self._access.allows(indexed.acl_ref, indexed.sensitivity):
            raise NotVisible(node_id)
        node = self._repo.find(node_id)
        if node is None:
            # Indexed but absent: drift, not permission. Same answer regardless.
            raise NotVisible(node_id)
        return node

    def sensitivity_of(self, node_id: str) -> Sensitivity:
        """The tier of a node this session can see, for inheritance arithmetic."""
        return self.visible(node_id).frontmatter.acl.sensitivity

    # ---- the one write -------------------------------------------------

    def propose(self, record: ProposalRecord, node: Node) -> ProposalRecord:
        """Store a proposal, after the checks that make it safe to store.

        Order matters. The ACL check runs before anything is written, so a
        blocked attempt leaves an audit record and no file — a rejected write
        that still lands bytes in ``_proposals/`` is a rejected write that a
        reviewer can accept.
        """
        if not self.may_propose:
            self._audit.record(
                actor=self._principal,
                action=Action.WRITE_NODE,
                outcome=Outcome.REFUSED,
                node_ids=[record.target],
                detail="session is read-only",
            )
            raise AgentWriteRefused(
                f"this session may not propose changes (read-only): {record.target}"
            )
        self._check_no_widening(record, node)
        return self._proposals.put(record, node)

    def _check_no_widening(self, record: ProposalRecord, node: Node) -> None:
        """Invariant 6, checked before the bytes exist.

        Two directions, both real:

        * The proposed node may not be looser than the node it replaces. An
          agent cannot relabel a restricted page as internal.
        * The proposed node may not be looser than the narrowest input the
          proposal draws on — which for an edge includes the *object*, because
          asserting ``internal-doc --owns--> restricted-node`` at internal tier
          publishes the existence of restricted content to everyone holding the
          internal grant.
        """
        proposed = node.frontmatter.acl.sensitivity
        required = record.sensitivity
        if _looser(proposed, required):
            self._blocked(record.target, f"{proposed} proposed, inputs require {required}")
            raise AclWideningBlocked(
                f"{record.target}: a proposal derived from {required} content may not be "
                f"written at {proposed}; widening is blocked, not queued"
            )

    def _blocked(self, target: str, detail: str) -> None:
        self._audit.record(
            actor=self._principal,
            action=Action.ACL_WIDENING_BLOCKED,
            outcome=Outcome.BLOCKED,
            node_ids=[target],
            detail=detail,
        )

    # ---- helpers the tools need ----------------------------------------

    def inherited_tier(self, *node_ids: str) -> Sensitivity:
        """The tier a proposal touching these nodes must carry.

        ``narrowest`` fails closed on an empty input (restricted), which is the
        right answer for a proposal whose inputs we could not determine.
        """
        return narrowest(self.sensitivity_of(n) for n in node_ids)

    def base_sha256(self, node: Node) -> str:
        return content_sha256(dump_node(node))

    def check_patch(self, patch: dict[str, Any], target: str) -> None:
        """Refuse a patch that names a field outside :data:`PATCHABLE`.

        An ACL field gets its own refusal and its own audit action, because
        "the agent tried to widen an ACL" and "the agent sent a typo" are
        different events and only one of them is worth waking someone for.
        """
        unknown = set(patch) - PATCHABLE
        if not unknown:
            return
        acl_attempt = unknown & ACL_FIELDS
        if acl_attempt:
            self._blocked(target, f"patch named acl field(s): {sorted(acl_attempt)}")
            raise AclWideningBlocked(
                f"{target}: an agent may not set {sorted(acl_attempt)}; a node's ACL is "
                f"inherited from its source, never proposed"
            )
        self._audit.record(
            actor=self._principal,
            action=Action.PATCH_FIELD_REFUSED,
            outcome=Outcome.REFUSED,
            node_ids=[target],
            detail=f"unpatchable field(s): {sorted(unknown)}",
        )
        raise PatchFieldRefused(
            f"{target}: {sorted(unknown)} is not agent-writable; "
            f"writable fields are {sorted(PATCHABLE)}"
        )

    def check_generated_regions(self, stored: Node, proposed: Node) -> None:
        """Invariant 13 for the agent path.

        A machine writer may touch only the *interior* of a generated fence, and
        an agent proposal is not the machine that owns those fences — it is
        proposing human-surface text. So every generated region must survive the
        proposal byte-identically. The check is the same one the live editor
        runs on human edits, for the same reason: the caller is not a trust
        boundary.
        """
        try:
            check_generated_regions(stored.body, proposed.body)
        except FenceViolation as exc:
            self._audit.record(
                actor=self._principal,
                action=Action.WRITE_NODE,
                outcome=Outcome.REFUSED,
                node_ids=[stored.id],
                detail=f"generated region touched: {exc}",
            )
            raise AgentWriteRefused(
                f"{stored.id}: a proposal may not change a generated region ({exc})"
            ) from exc

    # ---- the wall ------------------------------------------------------
    #
    # Present, refusing, and audited. Each one is a method a future tool author
    # would reach for, and each one fails at the boundary rather than deep in a
    # store write with half a node already on disk.

    def put(self, node: Node, **_: object) -> NoReturn:
        self._refuse("put", getattr(node, "id", ""))

    def put_proposal(self, *_: object, **__: object) -> NoReturn:
        # Refused even though it writes to `_proposals/`: it skips the ACL
        # inheritance check and the queue row, so it would produce an
        # unreviewable proposal that no widening check ever saw.
        self._refuse("put_proposal", "")

    def tombstone(self, node_id: str, **_: object) -> NoReturn:
        self._refuse("tombstone", node_id)

    def redirect(self, old_id: str, new_id: str, **_: object) -> NoReturn:
        self._refuse("redirect", old_id)

    def _refuse(self, operation: str, node_id: str) -> NoReturn:
        self._audit.record(
            actor=self._principal,
            action=Action.GRAPH_WRITE_REFUSED,
            outcome=Outcome.REFUSED,
            node_ids=[node_id] if node_id else [],
            detail=f"direct {operation} from an agent session",
        )
        raise AgentWriteRefused(
            f"agents never write to the graph: {operation}"
            f"{f' on {node_id}' if node_id else ''} is a proposal or it is nothing"
        )


def _looser(candidate: Sensitivity, floor: Sensitivity) -> bool:
    """Is `candidate` a *less* restrictive tier than `floor`?

    Expressed through `at_least` rather than a private rank table: the ordering
    of tiers has exactly one definition (`schemas.acl`), and a second copy here
    would be a second thing to keep in sync with it.
    """
    return candidate is not floor and at_least(candidate, floor)
