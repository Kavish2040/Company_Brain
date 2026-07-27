"""Principal resolution and the visible-ACL-set computation.

Invariant 5: every retrieval path takes an explicit Principal. Invariant 8: an
agent's effective visibility is the *intersection* of its own grants and the
grants of the human who invoked it — an agent must never be able to see more
than the person it is acting for, and must never be able to claim an identity.

`elevate()` is the single audited bypass. It exists for index rebuild, which has
to read every node, and it is never reachable from a request path.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from company_brain.schemas.acl import Principal, PrincipalKind, Sensitivity


@dataclass(slots=True)
class GrantTable:
    """Who can see which ACL refs.

    Mirrors the source systems and is therefore *eventually consistent by
    construction*: a channel membership change is visible here only after the
    next sync. That lag is a real leak window, not an implementation defect —
    every mirrored-permission system has one. The honest posture is to bound it
    and measure it, which is what `synced_at` is for in the Postgres schema.
    """

    _direct: dict[str, set[str]] = field(default_factory=dict)
    _members: dict[str, set[str]] = field(default_factory=dict)
    _tiers: dict[str, set[Sensitivity]] = field(default_factory=dict)
    # Agents must be registered before they can see anything. An unregistered
    # agent id is denied outright rather than falling back to the human's set,
    # so a typo'd or spoofed agent name fails closed.
    _agents: dict[str, bool] = field(default_factory=dict)

    def grant(self, principal_id: str, acl_ref: str, tier: Sensitivity) -> None:
        self._direct.setdefault(principal_id, set()).add(acl_ref)
        self._tiers.setdefault(principal_id, set()).add(tier)

    def revoke(self, principal_id: str, acl_ref: str) -> None:
        self._direct.get(principal_id, set()).discard(acl_ref)

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

    def visible_refs(self, principal: Principal) -> frozenset[str]:
        """Expand a principal's grants through group membership.

        A delegated agent can never exceed the human it acts for. That cap is
        the invariant; how the agent's own side is computed depends on how it
        was registered.
        """
        if principal.delegated_by is None:
            return self._expand(principal.id)

        human = self._expand(principal.delegated_by)
        inherit = self._agents.get(principal.id)
        if inherit is None:
            return frozenset()  # unregistered agent: fail closed
        return human if inherit else self._expand(principal.id) & human

    def visible_tiers(self, principal: Principal) -> frozenset[Sensitivity]:
        if principal.delegated_by is None:
            return self._tiers_for(principal.id)

        human = self._tiers_for(principal.delegated_by)
        inherit = self._agents.get(principal.id)
        if inherit is None:
            return frozenset()
        return human if inherit else self._tiers_for(principal.id) & human

    def _expand(self, principal_id: str) -> frozenset[str]:
        refs = set(self._direct.get(principal_id, ()))
        for group in self._members.get(principal_id, ()):
            refs |= self._direct.get(group, set())
        return frozenset(refs)

    def _tiers_for(self, principal_id: str) -> frozenset[Sensitivity]:
        tiers = set(self._tiers.get(principal_id, ()))
        for group in self._members.get(principal_id, ()):
            tiers |= self._tiers.get(group, set())
        return frozenset(tiers)


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
    """Answers 'can this principal see this node?' — and nothing else."""

    def __init__(self, grants: GrantTable, principal: Principal) -> None:
        self.principal = principal
        self.elevated = is_elevated(principal)
        self.refs = frozenset() if self.elevated else grants.visible_refs(principal)
        self.tiers = frozenset() if self.elevated else grants.visible_tiers(principal)

    def allows(self, acl_ref: str, sensitivity: Sensitivity) -> bool:
        if self.elevated:
            return True
        return acl_ref in self.refs and sensitivity in self.tiers

    def filter_ids(self, pairs: Iterable[tuple[str, str, Sensitivity]]) -> list[str]:
        return [nid for nid, ref, tier in pairs if self.allows(ref, tier)]
