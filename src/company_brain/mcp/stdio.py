"""MCP stdio server.

Identity binding is the whole point of this file. Invariant 8 says the principal
comes from the authenticated session and is never a tool parameter — for a stdio
server the *process* is the session, so the principal is fixed at startup and no
tool below accepts one. A model calling these tools has no argument it can pass
to become somebody else.

The agent's effective visibility is the intersection of its own grants and the
grants of the human who launched it. Both are set here, once.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from company_brain.app import build_app
from company_brain.mcp.server import McpTools, Session

INSTRUCTIONS = """\
company_brain exposes a company's knowledge graph: documents, people, teams,
tools, processes and decisions, linked by typed edges.

Every result is filtered by the permissions of the human this session acts for.
If something is not returned, either it does not exist or you may not see it —
the two are deliberately indistinguishable, so do not infer existence from a
missing result.

read_node returns a permission-projected view, never the stored file.

You cannot modify the graph. write_node and propose_edge create proposals for
human review and return a proposal id; nothing you send changes what other
readers see until a person accepts it.
"""


def build_server(
    store: Path, *, agent_id: str, delegated_by: str, name: str = "company_brain"
) -> FastMCP:
    app = build_app(store)
    nodes = app.load_index()
    # Register before the session exists: an unregistered agent is denied
    # everything, which is correct but would silently return empty results.
    # `inherit=True` caps this agent at the invoking human's grants.
    app.grants.register_agent(agent_id, inherit=True)
    session = Session(app=app, agent_id=agent_id, delegated_by=delegated_by)
    tools = McpTools(session)

    server: FastMCP = FastMCP(
        name,
        instructions=INSTRUCTIONS
        + f"\nActing for: {delegated_by}. "
        + f"Visible sources: {len(session.access.refs)}. Indexed chunks: {nodes}.",
    )

    # Note the absence of a principal argument on every signature below.

    @server.tool(
        description=(
            "Search the company knowledge graph. Hybrid lexical + vector "
            "retrieval, filtered to what this session may see."
        )
    )
    def search(query: str, limit: int = 8) -> list[dict[str, Any]]:
        return tools.search(query, limit=limit)

    @server.tool(
        description=(
            "Follow typed edges from a node. Optionally restrict to predicates "
            "such as owns, authored_by, handoff_to, depends_on, mentions. "
            "Each hop is permission-checked independently."
        )
    )
    def traverse(
        node_id: str, predicates: list[str] | None = None, limit: int = 20
    ) -> list[dict[str, str]]:
        return tools.traverse(node_id, predicates=predicates, limit=limit)

    @server.tool(
        description=(
            "Read one node: title, body, and the relations visible to this "
            "session. Raises not-found for nodes you may not see."
        )
    )
    def read_node(node_id: str) -> dict[str, Any]:
        return tools.read_node(node_id)

    @server.tool(
        description=(
            "Propose a change to a node's body. Creates a proposal for human "
            "review; does NOT modify the graph."
        )
    )
    def write_node(node_id: str, body: str) -> dict[str, str]:
        return tools.write_node(node_id, {"body": body})

    @server.tool(
        description=(
            "Propose a new typed edge, with a verbatim quote as evidence. "
            "Creates a proposal for human review; does NOT modify the graph."
        )
    )
    def propose_edge(
        subject: str, predicate: str, object: str, evidence_quote: str
    ) -> dict[str, str]:
        return tools.propose_edge(subject, predicate, object, evidence_quote)

    return server


def serve(store: Path, *, agent_id: str, delegated_by: str) -> None:
    build_server(store, agent_id=agent_id, delegated_by=delegated_by).run("stdio")
