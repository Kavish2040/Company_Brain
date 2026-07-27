"""MCP stdio server.

Identity binding is the whole point of this file. Invariant 8 says the principal
comes from the authenticated session and is never a tool parameter — for a stdio
server the *process* is the session, so the principal is fixed at startup and no
tool below accepts one. A model calling these tools has no argument it can pass
to become somebody else.

The agent's effective visibility is the intersection of its own grants and the
grants of the human who launched it. Both are set here, once.

That binding now covers writes as well as reads. A proposal carries the agent's
identity *and* the human's into the review queue, so the reviewer sees "agent-x,
acting for the CEO" rather than an anonymous suggestion — and an agent whose
human cannot see a node cannot propose against it either, because the same
intersection gates both.
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

Two things are refused outright rather than queued: anything that would make
content visible to more people than its sources allow, and any attempt to set a
node's acl. Propose the claim; the permissions are not yours to state.

Every call is logged with this session's identity and the node ids it touched.
"""


def build_server(
    store: Path,
    *,
    agent_id: str,
    delegated_by: str,
    read_only: bool = False,
    name: str = "company_brain",
) -> FastMCP:
    app = build_app(store)
    nodes = app.load_index()
    # `Session.bind` registers the agent and opens the audit trail. Registration
    # has to happen before the session exists: an unregistered agent is denied
    # everything, which is correct but would surface as silently empty results.
    session = Session.bind(
        app, agent_id=agent_id, delegated_by=delegated_by, read_only=read_only
    )
    tools = McpTools(session)

    server: FastMCP = FastMCP(
        name,
        instructions=INSTRUCTIONS
        + f"\nActing for: {delegated_by}. "
        + f"Visible sources: {len(session.access.refs)}. Indexed chunks: {nodes}."
        + (" This session is read-only." if read_only else ""),
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

    if not read_only:

        @server.tool(
            description=(
                "Propose a change to a node's body, or to its aliases. Creates a "
                "proposal for human review; does NOT modify the graph. The node's "
                "permissions are inherited and cannot be set here."
            )
        )
        def write_node(
            node_id: str, body: str | None = None, aliases: list[str] | None = None
        ) -> dict[str, str]:
            # Assembled into a patch here rather than exposing a free-form dict:
            # a dict parameter invites a model to try `acl`, and the refusal —
            # while real — is a worse experience than a schema that never
            # offered the field.
            patch: dict[str, Any] = {}
            if body is not None:
                patch["body"] = body
            if aliases is not None:
                patch["aliases"] = aliases
            return tools.write_node(node_id, patch)

        @server.tool(
            description=(
                "Propose a new typed edge, with a verbatim quote as evidence. "
                "Creates a proposal for human review; does NOT modify the graph. "
                "Both ends must be visible to this session."
            )
        )
        def propose_edge(
            subject: str, predicate: str, object: str, evidence_quote: str
        ) -> dict[str, str]:
            return tools.propose_edge(subject, predicate, object, evidence_quote)

    return server


def serve(store: Path, *, agent_id: str, delegated_by: str, read_only: bool = False) -> None:
    build_server(store, agent_id=agent_id, delegated_by=delegated_by, read_only=read_only).run(
        "stdio"
    )
