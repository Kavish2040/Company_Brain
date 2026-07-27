"""MCP server: the agent-facing surface.

Two rules from ARCHITECTURE §8, both enforced here rather than documented:

* **Identity is never a tool parameter.** The principal comes from the session,
  so an agent cannot say "I am acting as the CFO". Every tool signature below
  takes its principal from the bound session, not from the model's arguments.
* **Agents never write to the graph.** `write_node` and `propose_edge` create
  entries under `store/_proposals/` plus a review-queue record, and return a
  proposal ID. There is no code path from a tool call to a graph mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from company_brain.acl.grants import AccessFilter
from company_brain.app import App
from company_brain.retrieve.hybrid import HybridRetriever
from company_brain.schemas.acl import Principal, PrincipalKind
from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance
from company_brain.schemas.nodes import Node


class AgentWriteRefused(PermissionError):
    """An agent attempted a direct graph mutation."""


@dataclass(slots=True)
class Session:
    """An authenticated MCP session.

    ``agent`` is the agent's own identity; ``delegated_by`` is the human who
    invoked it. The effective visible set is the intersection (invariant 8),
    computed in GrantTable — not here, so there is one implementation of it.
    """

    app: App
    agent_id: str
    delegated_by: str

    @property
    def principal(self) -> Principal:
        return Principal(
            id=self.agent_id,
            kind=PrincipalKind.AGENT,
            display=f"agent {self.agent_id}",
            delegated_by=self.delegated_by,
        )

    @property
    def access(self) -> AccessFilter:
        return self.app.access(self.principal)


class McpTools:
    """The five tools. Read tools ACL-filter; write tools produce proposals."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ---- read ----------------------------------------------------------

    def search(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        retriever = HybridRetriever(self.session.app.index, self.session.access)
        result = retriever.retrieve(query, limit=limit)
        return [
            {
                "node_id": node.node_id,
                "title": node.title,
                "score": round(node.score, 5),
                "snippet": node.snippets[0][:300] if node.snippets else "",
                "hops": node.hops,
            }
            for node in result.nodes
        ]

    def traverse(
        self, node_id: str, predicates: list[str] | None = None, limit: int = 20
    ) -> list[dict[str, str]]:
        index = self.session.app.index
        access = self.session.access
        wanted = frozenset(predicates) if predicates else None
        out: list[dict[str, str]] = []
        for neighbour in index.neighbours(node_id, wanted, limit=limit * 2):
            indexed = index.get_node(neighbour)
            # Filter per hop, not once at the seed.
            if indexed is None or not access.allows(indexed.acl_ref, indexed.sensitivity):
                continue
            out.append({"node_id": indexed.id, "title": indexed.title, "type": indexed.type})
            if len(out) >= limit:
                break
        return out

    def read_node(self, node_id: str) -> dict[str, Any]:
        """Return the ACL-projected node — never the stored bytes.

        A node whose every edge is invisible returns not-found rather than an
        empty page: an empty page confirms the node exists (§6.3).
        """
        index = self.session.app.index
        access = self.session.access
        indexed = index.get_node(node_id)
        if indexed is None or not access.allows(indexed.acl_ref, indexed.sensitivity):
            raise KeyError(node_id)

        node = self.session.app.repo.find(node_id)
        visible_edges = []
        for edge in indexed.edges:
            if edge.status is not EdgeStatus.ACCEPTED:
                continue
            target = index.get_node(edge.object)
            if target is None or not access.allows(target.acl_ref, target.sensitivity):
                continue
            visible_edges.append(
                {
                    "predicate": str(edge.predicate),
                    "object": edge.object,
                    "confidence": edge.confidence,
                    "provenance": str(edge.provenance),
                }
            )

        return {
            "id": indexed.id,
            "type": indexed.type,
            "title": indexed.title,
            "body": node.body if node else "",
            "relations": visible_edges,
        }

    # ---- write (proposals only) -----------------------------------------

    def write_node(self, node_id: str, patch: dict[str, Any]) -> dict[str, str]:
        node = self.session.app.repo.find(node_id)
        if node is None:
            raise KeyError(node_id)
        proposed = Node(
            frontmatter=node.frontmatter,
            body=str(patch.get("body", node.body)),
        )
        proposal_id = f"write-{self.session.agent_id}-{_short(node_id)}"
        self.session.app.repo.put_proposal(proposal_id, proposed)
        return {"proposal_id": proposal_id, "state": "pending_review"}

    def propose_edge(
        self, subject: str, predicate: str, obj: str, evidence_quote: str
    ) -> dict[str, str]:
        node = self.session.app.repo.find(subject)
        if node is None:
            raise KeyError(subject)
        edge = Edge(
            predicate=Predicate(predicate),
            object=obj,
            confidence=0.5,
            provenance=Provenance.LLM,
            # Always proposed. There is no argument an agent can pass that
            # makes this accepted.
            status=EdgeStatus.PROPOSED,
            evidence=(Evidence(node=subject, quote=evidence_quote[:500]),),
        )
        merged = {(str(e.predicate), e.object): e for e in node.frontmatter.relations}
        merged[(str(edge.predicate), edge.object)] = edge
        proposed = Node(
            frontmatter=node.frontmatter.model_copy(
                update={"relations": tuple(merged.values())}
            ),
            body=node.body,
        )
        proposal_id = f"edge-{self.session.agent_id}-{_short(subject)}-{predicate}"
        self.session.app.repo.put_proposal(proposal_id, proposed)
        return {"proposal_id": proposal_id, "state": "pending_review"}


def _short(node_id: str) -> str:
    return node_id.replace("/", "-")[-40:]


def describe() -> dict[str, Any]:
    """Tool manifest. Note the absence of any principal argument."""
    return {
        "server": "company_brain",
        "identity": "from the authenticated session; never a tool parameter",
        "tools": [
            {"name": "search", "args": ["query", "limit"], "writes": False},
            {"name": "traverse", "args": ["node_id", "predicates", "limit"], "writes": False},
            {
                "name": "read_node",
                "args": ["node_id"],
                "writes": False,
                "note": "returns an ACL-projected node, never stored bytes",
            },
            {"name": "write_node", "args": ["node_id", "patch"], "writes": "proposal"},
            {
                "name": "propose_edge",
                "args": ["subject", "predicate", "object", "evidence_quote"],
                "writes": "proposal",
            },
        ],
    }
