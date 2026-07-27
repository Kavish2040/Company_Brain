"""Principal resolution and the visible-ACL-set computation.

Invariant 5: every retrieval path takes an explicit Principal. Invariant 8: an
agent's effective visibility is the *intersection* of its own grants and the
grants of the human who invoked it — an agent must never be able to see more
than the person it is acting for, and must never be able to claim an identity.

`elevate()` is the single audited bypass. It exists for index rebuild, which has
to read every node, and it is never reachable from a request path.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from company_brain.schemas.acl import Principal, PrincipalKind, Sensitivity, at_least


def _higher(a: Sensitivity, b: Sensitivity) -> Sensitivity:
    """The more permissive of two ceilings on the same ref."""
    return a if at_least(b, a) else b


def _lower(a: Sensitivity, b: Sensitivity) -> Sensitivity:
    """The less permissive of two ceilings — how an agent is capped by its human."""
    return b if at_least(b, a) else a


@dataclass(slots=True)
class GrantTable:
    """Who can see which ACL refs, and up to which sensitivity on each.

    A grant is a *pair*: (ref, ceiling). Storing the two halves in separate sets
    and testing them independently makes access a cross-product — one restricted
    channel would raise the ceiling on every other ref the principal holds, and
    revoking that channel would leave the raised ceiling behind. So the pairing
    is the storage format, and `_ceilings` is the only thing `AccessFilter` reads.

    Mirrors the source systems and is therefore *eventually consistent by
    construction*: a channel membership change is visible here only after the
    next sync. That lag is a real leak window, not an implementation defect —
    every mirrored-permission system has one. The honest posture is to bound it
    and measure it, which is what `synced_at` is for in the Postgres schema.
    """

    # principal -> ref -> ceiling. One entry per grant; no free-floating tiers.
    _direct: dict[str, dict[str, Sensitivity]] = field(default_factory=dict)
    _members: dict[str, set[str]] = field(default_factory=dict)
    # Agents must be registered before they can see anything. An unregistered
    # agent id is denied outright rather than falling back to the human's set,
    # so a typo'd or spoofed agent name fails closed.
    _agents: dict[str, bool] = field(default_factory=dict)

    def grant(self, principal_id: str, acl_ref: str, tier: Sensitivity) -> None:
        """Grant `acl_ref` up to `tier`. Re-granting raises that ref's ceiling only."""
        held = self._direct.setdefault(principal_id, {})
        current = held.get(acl_ref)
        held[acl_ref] = tier if current is None else _higher(current, tier)

    def revoke(self, principal_id: str, acl_ref: str) -> None:
        """Drop a grant. The ceiling goes with the ref — that is the point of the pairing."""
        self._direct.get(principal_id, {}).pop(acl_ref, None)

    def add_to_group(self, principal_id: str, group_id: str) -> None:
        self._members.setdefault(principal_id, set()).add(group_id)

    def register_agent(self, agent_id: str, *, inherit: bool) -> None:
        """Register an agent and declare how its ceiling is computed.

        ``inherit=True`` — the agent may see whatever the invoking human sees.
        ``inherit=False`` — the agent has its own grant list, and its view is the
        intersection of that list with the human's, so it can be scoped *below*
        the human but never above.

        Both forms are capped by the human. The distinction is only whether the
        agent carries an additional restriction of its own.
        """
        self._agents[agent_id] = inherit

    def is_registered_agent(self, agent_id: str) -> bool:
        return agent_id in self._agents

    def ceilings(self, principal: Principal) -> Mapping[str, Sensitivity]:
        """Every ref this principal can reach, mapped to its ceiling.

        A delegated agent can never exceed the human it acts for. That cap now
        applies per ref *and* per tier: an agent scoped to `internal` on a ref
        the human holds at `restricted` stays at `internal`, and vice versa.
        """
        if principal.delegated_by is None:
            return self._expand(principal.id)

        human = self._expand(principal.delegated_by)
        inherit = self._agents.get(principal.id)
        if inherit is None:
            return {}  # unregistered agent: fail closed
        if inherit:
            return human
        agent = self._expand(principal.id)
        return {ref: _lower(tier, human[ref]) for ref, tier in agent.items() if ref in human}

    def visible_refs(self, principal: Principal) -> frozenset[str]:
        """Which refs are reachable at all. Display and diagnostics only —
        never an access decision, which needs the ceiling too."""
        return frozenset(self.ceilings(principal))

    def snapshot(self) -> dict[str, frozenset[str]]:
        """Direct grants per principal, for reconciling against a source.

        Direct only — group-derived access is not something a connector can
        revoke, because it does not own the group.
        """
        return {p: frozenset(held) for p, held in self._direct.items() if held}

    def _expand(self, principal_id: str) -> dict[str, Sensitivity]:
        """Direct grants plus group-derived ones, keeping the highest ceiling per ref."""
        out = dict(self._direct.get(principal_id, {}))
        for group in self._members.get(principal_id, ()):
            for ref, tier in self._direct.get(group, {}).items():
                current = out.get(ref)
                out[ref] = tier if current is None else _higher(current, tier)
        return out


ELEVATED = Principal(id="system:reindex", kind=PrincipalKind.SERVICE, display="index rebuild")


def elevate() -> Principal:
    """The one audited full-access principal.

    Only the index builder may call this. It is not reachable from the API, MCP,
    or CLI ask paths; a test asserts those modules never import it.
    """
    return ELEVATED


def is_elevated(principal: Principal) -> bool:
    return principal.id == ELEVATED.id


class AccessFilter:
    """Answers 'can this principal see this node?' — and nothing else.

    This is the *only* implementation of that predicate. Callers pass the filter
    itself rather than its parts: handing out loose `refs` and `tiers` sets is
    what let the index re-derive the decision and drift from this one.
    """

    def __init__(self, grants: GrantTable, principal: Principal) -> None:
        self.principal = principal
        self.elevated = is_elevated(principal)
        self._ceilings: Mapping[str, Sensitivity] = (
            {} if self.elevated else grants.ceilings(principal)
        )
        # Reachable refs, for display and diagnostics. Not sufficient for a decision.
        self.refs = frozenset(self._ceilings)

    def ceiling(self, acl_ref: str) -> Sensitivity | None:
        """The highest tier this principal may read on `acl_ref`, if any."""
        return self._ceilings.get(acl_ref)

    def allows(self, acl_ref: str, sensitivity: Sensitivity) -> bool:
        if self.elevated:
            return True
        ceiling = self._ceilings.get(acl_ref)
        return ceiling is not None and at_least(sensitivity, ceiling)

    def filter_ids(self, pairs: Iterable[tuple[str, str, Sensitivity]]) -> list[str]:
        return [nid for nid, ref, tier in pairs if self.allows(ref, tier)]
