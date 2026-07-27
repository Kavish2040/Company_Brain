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
