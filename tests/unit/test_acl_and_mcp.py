"""Delegation, ACL drift, and the agent boundary.

ACL drift is the case the point-in-time enforcement tests miss. Grants mirror
source systems and are therefore eventually consistent by construction, so what
matters is not "is the filter applied" but "does a revoked grant stop mattering,
and does it stop mattering everywhere at once".
"""

from __future__ import annotations

import pytest

from company_brain.acl.grants import AccessFilter, GrantTable, elevate, is_elevated
from company_brain.schemas.acl import Principal, PrincipalKind, Sensitivity

INTERNAL = Sensitivity.INTERNAL
RESTRICTED = Sensitivity.RESTRICTED


def human(name: str) -> Principal:
    return Principal(id=name, kind=PrincipalKind.USER, display=name)


def agent(name: str, on_behalf_of: str) -> Principal:
    return Principal(id=name, kind=PrincipalKind.AGENT, display=name, delegated_by=on_behalf_of)


@pytest.fixture
def grants() -> GrantTable:
    table = GrantTable()
    table.grant("boss", "slack:channel:PUBLIC", INTERNAL)
    table.grant("boss", "slack:channel:SECRET", RESTRICTED)
    table.grant("staff", "slack:channel:PUBLIC", INTERNAL)
    return table


class TestDelegation:
    def test_unregistered_agent_sees_nothing(self, grants: GrantTable) -> None:
        # Fail closed: a typo'd or spoofed agent id must not inherit by accident.
        assert grants.visible_refs(agent("ghost", "boss")) == frozenset()

    def test_inheriting_agent_gets_the_humans_view(self, grants: GrantTable) -> None:
        grants.register_agent("helper", inherit=True)
        assert grants.visible_refs(agent("helper", "staff")) == {"slack:channel:PUBLIC"}

    def test_agent_can_never_exceed_the_human(self, grants: GrantTable) -> None:
        """Invariant 8. The agent itself holds the restricted channel; the human
        it acts for does not. The intersection must win."""
        grants.register_agent("privileged", inherit=False)
        grants.grant("privileged", "slack:channel:PUBLIC", INTERNAL)
        grants.grant("privileged", "slack:channel:SECRET", RESTRICTED)

        visible = grants.visible_refs(agent("privileged", "staff"))
        assert visible == {"slack:channel:PUBLIC"}
        assert "slack:channel:SECRET" not in visible

    def test_scoped_agent_can_be_narrower_than_the_human(self, grants: GrantTable) -> None:
        grants.register_agent("narrow", inherit=False)
        grants.grant("narrow", "slack:channel:PUBLIC", INTERNAL)
        # boss can see SECRET; this agent is deliberately scoped below them.
        assert grants.visible_refs(agent("narrow", "boss")) == {"slack:channel:PUBLIC"}

    def test_inheriting_agent_still_capped_by_tier(self, grants: GrantTable) -> None:
        grants.register_agent("helper", inherit=True)
        access = AccessFilter(grants, agent("helper", "staff"))
        assert not access.allows("slack:channel:SECRET", RESTRICTED)


class TestAclDrift:
    """Grant changes mid-flight — the failure that actually happens."""

    def test_revoking_a_grant_removes_access(self, grants: GrantTable) -> None:
        before = AccessFilter(grants, human("boss"))
        assert before.allows("slack:channel:SECRET", RESTRICTED)

        grants.revoke("boss", "slack:channel:SECRET")

        after = AccessFilter(grants, human("boss"))
        assert not after.allows("slack:channel:SECRET", RESTRICTED)

    def test_an_access_filter_is_a_snapshot_not_a_live_view(self, grants: GrantTable) -> None:
        """Documents the leak window rather than pretending it doesn't exist.

        AccessFilter resolves the visible set once, at construction. A revocation
        during an in-flight request is therefore NOT observed by that request.
        That is a deliberate consistency choice — re-resolving per hop would make
        a single answer's permission basis vary mid-computation — but it means
        the enforcement boundary is per-request, and callers must construct a
        fresh filter per request. The next test is the one that guards it.
        """
        stale = AccessFilter(grants, human("boss"))
        grants.revoke("boss", "slack:channel:SECRET")
        assert stale.allows("slack:channel:SECRET", RESTRICTED)

    def test_a_fresh_filter_reflects_the_revocation_immediately(
        self, grants: GrantTable
    ) -> None:
        grants.revoke("boss", "slack:channel:SECRET")
        assert not AccessFilter(grants, human("boss")).allows(
            "slack:channel:SECRET", RESTRICTED
        )

    def test_revocation_propagates_to_a_delegated_agent(self, grants: GrantTable) -> None:
        grants.register_agent("helper", inherit=True)
        assert AccessFilter(grants, agent("helper", "boss")).allows(
            "slack:channel:SECRET", RESTRICTED
        )

        grants.revoke("boss", "slack:channel:SECRET")

        # The agent's own registration is untouched; it must still lose access,
        # because the cap is the human's set and that set shrank.
        assert not AccessFilter(grants, agent("helper", "boss")).allows(
            "slack:channel:SECRET", RESTRICTED
        )

    def test_group_revocation_propagates(self, grants: GrantTable) -> None:
        grants.grant("finance-team", "gdrive:folder:LEDGER", RESTRICTED)
        grants.add_to_group("staff", "finance-team")
        assert AccessFilter(grants, human("staff")).allows("gdrive:folder:LEDGER", RESTRICTED)

        grants.revoke("finance-team", "gdrive:folder:LEDGER")
        assert not AccessFilter(grants, human("staff")).allows(
            "gdrive:folder:LEDGER", RESTRICTED
        )


class TestGrantPairing:
    """A grant is a (ref, ceiling) pair, and the two halves must stay married.

    Storing refs and tiers in separate sets makes `allows` a cross-product: hold
    one restricted channel and every other ref you hold is silently restricted
    too. Every test here fails against that shape, and the existing suite did
    not, because its fixtures map each tier to exactly one ref — so the ref check
    and the tier check could never disagree.
    """

    PUBLIC_CH = "slack:channel:PUBLIC"
    SECRET_CH = "slack:channel:SECRET"

    def test_a_tier_from_one_ref_does_not_apply_to_another(self, grants: GrantTable) -> None:
        """The escalation: adding someone to one restricted channel must not
        raise their ceiling on every other ref they already hold."""
        access = AccessFilter(grants, human("boss"))
        assert access.allows(self.SECRET_CH, RESTRICTED)
        assert not access.allows(self.PUBLIC_CH, RESTRICTED)

    def test_a_new_restricted_grant_does_not_widen_existing_refs(
        self, grants: GrantTable
    ) -> None:
        grants.grant("staff", "slack:channel:FINANCE", RESTRICTED)
        access = AccessFilter(grants, human("staff"))
        assert access.allows("slack:channel:FINANCE", RESTRICTED)
        # staff holds PUBLIC_CH at internal only; the finance grant is unrelated.
        assert not access.allows(self.PUBLIC_CH, RESTRICTED)
        assert not access.allows("gmail:mailbox:shared", RESTRICTED)

    def test_revoking_a_grant_takes_its_ceiling_with_it(self, grants: GrantTable) -> None:
        """The M2 case. `SyncEngine._sync_grants` calls revoke() when someone
        leaves a channel; a ceiling that outlives the ref makes that a no-op."""
        grants.grant("staff", "slack:channel:FINANCE", RESTRICTED)
        grants.revoke("staff", "slack:channel:FINANCE")

        access = AccessFilter(grants, human("staff"))
        assert not access.allows("slack:channel:FINANCE", RESTRICTED)
        assert not access.allows(self.PUBLIC_CH, RESTRICTED)
        assert access.ceiling("slack:channel:FINANCE") is None

    def test_regranting_higher_raises_only_that_ref(self, grants: GrantTable) -> None:
        grants.grant("staff", self.PUBLIC_CH, RESTRICTED)
        access = AccessFilter(grants, human("staff"))
        assert access.allows(self.PUBLIC_CH, RESTRICTED)
        assert not access.allows("slack:channel:OTHER", RESTRICTED)

    def test_a_ceiling_admits_everything_below_it(self, grants: GrantTable) -> None:
        """Tiers are ordered. A restricted grant must not refuse the public
        content sitting underneath it — `Sensitivity` says so in its docstring."""
        grants.grant("staff", "gdrive:folder:MIXED", RESTRICTED)
        access = AccessFilter(grants, human("staff"))
        assert access.allows("gdrive:folder:MIXED", RESTRICTED)
        assert access.allows("gdrive:folder:MIXED", INTERNAL)
        assert access.allows("gdrive:folder:MIXED", Sensitivity.PUBLIC)

    def test_a_low_ceiling_refuses_content_above_it(self, grants: GrantTable) -> None:
        """The direction that must stay closed: a Drive folder holding both
        internal and restricted files is exactly where M2 will find this."""
        grants.grant("staff", "gdrive:folder:MIXED", INTERNAL)
        access = AccessFilter(grants, human("staff"))
        assert access.allows("gdrive:folder:MIXED", INTERNAL)
        assert not access.allows("gdrive:folder:MIXED", RESTRICTED)

    def test_group_membership_takes_the_higher_ceiling_per_ref(
        self, grants: GrantTable
    ) -> None:
        grants.grant("staff", "gdrive:folder:LEDGER", INTERNAL)
        grants.grant("finance-team", "gdrive:folder:LEDGER", RESTRICTED)
        grants.add_to_group("staff", "finance-team")
        assert AccessFilter(grants, human("staff")).allows("gdrive:folder:LEDGER", RESTRICTED)

    def test_an_agent_is_capped_per_ref_not_just_per_ref_list(
        self, grants: GrantTable
    ) -> None:
        """Invariant 8 at tier granularity: the agent holds a ref at restricted
        that its human holds only at internal. The lower ceiling wins."""
        grants.grant("boss", "gdrive:folder:MIXED", INTERNAL)
        grants.register_agent("privileged", inherit=False)
        grants.grant("privileged", "gdrive:folder:MIXED", RESTRICTED)

        access = AccessFilter(grants, agent("privileged", "boss"))
        assert access.allows("gdrive:folder:MIXED", INTERNAL)
        assert not access.allows("gdrive:folder:MIXED", RESTRICTED)

    def test_an_agent_below_its_human_stays_below(self, grants: GrantTable) -> None:
        grants.grant("boss", "gdrive:folder:MIXED", RESTRICTED)
        grants.register_agent("narrow", inherit=False)
        grants.grant("narrow", "gdrive:folder:MIXED", INTERNAL)

        access = AccessFilter(grants, agent("narrow", "boss"))
        assert access.allows("gdrive:folder:MIXED", INTERNAL)
        assert not access.allows("gdrive:folder:MIXED", RESTRICTED)


class TestOneEnforcementPoint:
    """The index must ask the filter, not re-implement it.

    `MemoryIndex` used to carry its own copy of the predicate, and retrieval
    handed it loose ref and tier sets — so fixing `allows` alone would leave the
    search path leaking. A `PostgresIndex` would have made it three copies.
    """

    def test_search_honours_the_per_ref_ceiling(self) -> None:
        from company_brain.index.base import IndexedNode
        from company_brain.index.memory import MemoryIndex

        grants = GrantTable()
        grants.grant("reader", "slack:channel:OPEN", INTERNAL)
        grants.grant("reader", "slack:channel:VAULT", RESTRICTED)
        access = AccessFilter(grants, human("reader"))

        def node(node_id: str, ref: str, tier: Sensitivity) -> IndexedNode:
            return IndexedNode(
                id=node_id,
                type="Document",
                title="compensation planning",
                acl_ref=ref,
                sensitivity=tier,
                status="active",
                content_sha256="",
                edges=(),
            )

        index = MemoryIndex()
        index.rebuild(
            [
                # Same tier, different refs: allowed on VAULT, not on OPEN.
                (node("documents/vault", "slack:channel:VAULT", RESTRICTED), "compensation"),
                (node("documents/open", "slack:channel:OPEN", RESTRICTED), "compensation"),
            ]
        )

        found = {h.chunk.node_id for h in index.search_lexical("compensation", access, 10)}
        assert "documents/vault" in found
        assert "documents/open" not in found, "index applied a tier it was not granted on"

    def test_the_index_cannot_be_handed_loose_sets(self) -> None:
        """A guard against the old shape coming back by way of a new backend."""
        import inspect

        from company_brain.index.base import Index

        for name in ("search_vector", "search_lexical"):
            params = set(inspect.signature(getattr(Index, name)).parameters)
            assert "visibility" in params, f"{name} must take the filter itself"
            assert not (params & {"refs", "tiers", "elevated"}), (
                f"{name} takes ACL parts again: {params}"
            )


class TestElevation:
    def test_elevated_principal_sees_everything(self) -> None:
        access = AccessFilter(GrantTable(), elevate())
        assert access.allows("anything:at:all", RESTRICTED)

    def test_elevation_is_recognisable(self) -> None:
        assert is_elevated(elevate())
        assert not is_elevated(human("boss"))

    def test_request_paths_never_call_elevate(self) -> None:
        """`elevate()` is the one audited bypass; it must stay out of the paths
        that serve a user or an agent.

        Matches the call and the import specifically. The `elevated` *flag* on
        AccessFilter is a legitimate read — the retriever has to know whether to
        skip filtering — so a bare substring check would fail on correct code.
        """
        import ast
        import inspect

        from company_brain.mcp import server as mcp_server
        from company_brain.mcp import stdio as mcp_stdio
        from company_brain.retrieve import hybrid
        from company_brain.synthesize import answer

        for module in (mcp_server, mcp_stdio, hybrid, answer):
            tree = ast.parse(inspect.getsource(module))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    assert node.func.id != "elevate", (
                        f"{module.__name__} calls elevate() in a request path"
                    )
                if isinstance(node, ast.ImportFrom):
                    names = {a.name for a in node.names}
                    assert "elevate" not in names, f"{module.__name__} imports elevate()"


class TestMcpToolSurface:
    def test_no_tool_accepts_a_principal(self) -> None:
        """Invariant 8 at the schema level: there must be no argument a model
        can pass to change who it is."""
        import inspect

        from company_brain.mcp.server import McpTools

        forbidden = {"principal", "principal_id", "user", "user_id", "as_user", "acl"}
        for name, method in inspect.getmembers(McpTools, inspect.isfunction):
            if name.startswith("_"):
                continue
            params = set(inspect.signature(method).parameters) - {"self"}
            assert not (params & forbidden), f"{name} accepts identity: {params & forbidden}"

    def test_manifest_advertises_write_tools_as_proposals(self) -> None:
        from company_brain.mcp.server import describe

        manifest = describe()
        writes = {t["name"]: t["writes"] for t in manifest["tools"]}
        assert writes["write_node"] == "proposal"
        assert writes["propose_edge"] == "proposal"
        assert writes["search"] is False
