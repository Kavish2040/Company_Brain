"""M3 acceptance: agents contribute, and cannot corrupt.

The ROADMAP's criteria for this half of the milestone, each asserted end to end
rather than at the unit that implements it:

1. an agent attempting a direct graph write is rejected, and the attempt is
   audited;
2. an agent attempting to widen an ACL is blocked, not queued;
3. a reviewer processes 50 queued proposals in under 15 minutes without opening
   a terminal.

The third is the odd one out — it is a *usability* claim, and it is the one the
other two are in tension with, because every additional guard is another thing
between a reviewer and a decision. So it is tested as the ROADMAP states it:
fifty items, decided over HTTP only, on a wall clock. The budget is 18 seconds
per item for a human to read evidence and press a key; what is measured here is
how much of that the system spends on itself.

The corpus is the real one, ingested cold, because the queue's shape at 201
documents is the point — a review UI that works on three proposals and not on
three hundred has not been tested.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from company_brain.app import build_app, cached_extractor
from company_brain.audit.log import Action, Outcome, Surface
from company_brain.corpus.generate import generate
from company_brain.mcp.guard import AclWideningBlocked, AgentWriteRefused
from company_brain.mcp.server import McpTools, Session
from company_brain.review.proposals import ProposalState, ProposalStore
from company_brain.schemas.acl import Sensitivity
from company_brain.schemas.nodes import Node

pytestmark = pytest.mark.acceptance

# 15 minutes is the ROADMAP's budget for a human working 50 items. Machine time
# has to be a rounding error inside it, or the reviewer is waiting rather than
# reviewing. 60 seconds of it is generous and still a 15x margin.
MACHINE_BUDGET_SECONDS = 60.0
BATCH = 50


@pytest.fixture(scope="module")
def store(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The real corpus, ingested once for the module."""
    base = tmp_path_factory.mktemp("m3")
    corpus, store_root = base / "corpus", base / "store"
    generate(corpus)
    app = build_app(store_root)
    from company_brain.connectors.local_fs import LocalIngest

    ingest = LocalIngest(
        app.repo, app.registry, cached_extractor(app, store_root, frozen=False)
    )
    ingest.run(corpus)
    return store_root


@pytest.fixture
def agent(store: Path) -> tuple[McpTools, Any]:
    """A live MCP session over the ingested corpus, acting for the CEO."""
    app = build_app(store)
    app.load_index()
    session = Session.bind(app, agent_id="agent-researcher", delegated_by="ceo")
    return McpTools(session), app


def a_restricted_node(app: Any) -> Node:
    """A node only the CEO can see. The corpus plants one deliberately."""
    for node in app.repo.walk():
        if node.frontmatter.acl.sensitivity is Sensitivity.RESTRICTED:
            return node
    pytest.skip("the corpus has no restricted node to widen against")


def an_internal_node(app: Any) -> Node:
    for node in app.repo.walk():
        if (
            node.frontmatter.acl.sensitivity is Sensitivity.INTERNAL
            and node.frontmatter.type.value != "Document"
        ):
            return node
    raise AssertionError("no internal entity node in the corpus")


class TestCriterionOneDirectWritesAreAudited:
    def test_a_direct_graph_write_is_rejected_and_audited(
        self, agent: tuple[McpTools, Any]
    ) -> None:
        tools, app = agent
        target = an_internal_node(app)

        with pytest.raises(AgentWriteRefused):
            tools.session.store.put(target)

        trail = app.audit(Surface.MCP).read(limit=20, action=Action.GRAPH_WRITE_REFUSED)
        assert trail, "the attempt left no audit record"
        assert trail[0].actor == "agent-researcher"
        assert trail[0].delegated_by == "ceo"
        assert trail[0].outcome is Outcome.REFUSED
        assert target.id in trail[0].node_ids

    def test_the_audit_trail_names_nodes_and_never_content(
        self, agent: tuple[McpTools, Any]
    ) -> None:
        """Invariant 15 against the real corpus, where the bodies are long
        enough that a leak would be obvious and a truncation would not."""
        tools, app = agent
        hits = tools.search("vendor renewals")
        assert hits

        node = app.repo.get(hits[0]["node_id"])
        words = [w for w in node.body.split() if len(w) > 12][:5]

        serialized = "\n".join(str(r.to_dict()) for r in app.audit(Surface.MCP).scan())
        for word in words:
            assert word not in serialized, f"document text {word!r} reached the audit log"
        assert node.id in serialized


class TestCriterionTwoWideningIsBlocked:
    def test_an_edge_into_restricted_content_is_blocked_not_queued(
        self, agent: tuple[McpTools, Any]
    ) -> None:
        tools, app = agent
        secret = a_restricted_node(app)
        public_side = an_internal_node(app)
        proposals = ProposalStore(app.repo)
        before = len(proposals.records(state=ProposalState.PENDING))

        with pytest.raises(AclWideningBlocked):
            tools.propose_edge(public_side.id, "mentions", secret.id, "an evidence quote")

        after = proposals.records(state=ProposalState.PENDING)
        assert len(after) == before, "a widening attempt reached the review queue"
        blocked = app.audit(Surface.MCP).read(limit=5, action=Action.ACL_WIDENING_BLOCKED)
        assert blocked and blocked[0].outcome is Outcome.BLOCKED

    def test_the_agent_can_still_read_what_its_human_can(
        self, agent: tuple[McpTools, Any]
    ) -> None:
        """The block is about *writing* across a tier boundary. An agent
        delegated by the CEO reads restricted content perfectly well — if this
        failed, the test above would be proving nothing more than "the agent
        cannot see it"."""
        tools, app = agent
        secret = a_restricted_node(app)
        assert tools.read_node(secret.id)["id"] == secret.id


@pytest.fixture(scope="module")
def seeded(store: Path) -> int:
    """A realistic mixed queue: extraction's leftovers plus an agent's work.

    Cold ingest of this corpus leaves 32 proposed edges — the §11 gates doing
    their job, and short of the 50 the criterion names. The rest come from where
    the ROADMAP's demo says they come from: an agent pointed at the MCP server,
    proposing edges with evidence. A queue of one kind would not test the thing
    the reviewer actually faces, which is a queue of both.
    """
    app = build_app(store)
    app.load_index()
    tools = McpTools(Session.bind(app, agent_id="agent-seeder", delegated_by="ceo"))

    subjects = [
        n.id
        for n in app.repo.walk("Process")
        if n.frontmatter.acl.sensitivity is Sensitivity.INTERNAL
    ]
    objects = [
        n.id
        for n in app.repo.walk("Person")
        if n.frontmatter.acl.sensitivity is Sensitivity.INTERNAL
    ]
    assert subjects and objects, "the corpus has no internal entities to link"

    # The cross product, not a modular walk: proposal IDs are content-addressed,
    # so a repeated (subject, object) pair collapses into one queue entry — which
    # is the right behaviour and a very confusing way to end up with a short
    # queue.
    pairs = [(s, o) for s in subjects for o in objects if s != o]
    assert len(pairs) >= 25, f"only {len(pairs)} distinct links available"

    for index, (subject, obj) in enumerate(pairs[:25]):
        tools.propose_edge(subject, "mentions", obj, f"evidence line {index}")
    return 25


class TestCriterionThreeFiftyProposalsWithoutATerminal:
    @pytest.fixture
    def client(self, store: Path, seeded: int) -> Iterator[TestClient]:
        from company_brain.api.app import _app, api, get_app

        instance = build_app(store)
        instance.load_index()
        api.dependency_overrides[get_app] = lambda: instance
        with TestClient(api) as test_client:
            yield test_client
        api.dependency_overrides.clear()
        _app.cache_clear()

    def test_the_queue_arrives_with_its_evidence_in_one_request(
        self, client: TestClient
    ) -> None:
        """A gate whose evidence the reviewer cannot check is not a gate — and a
        UI that needs a second request per item to show it cannot spend 18
        seconds an item."""
        response = client.get("/api/review?limit=200", headers={"X-Principal": "ceo"})
        assert response.status_code == 200
        items = response.json()
        assert len(items) >= BATCH, f"the queue holds only {len(items)} items"

        for item in items[:BATCH]:
            assert item["summary"]
            assert item["added_relations"] or item["removed_relations"] or item["body_diff"], (
                f"{item['key']} has nothing to review"
            )
        assert any(item["quote"] for item in items[:BATCH])

    def test_agent_proposals_arrive_attributed(self, client: TestClient) -> None:
        """A suggestion nobody can attribute is a suggestion nobody should
        accept — the reviewer needs to know an agent wrote this, and for whom."""
        items = client.get("/api/review?limit=200", headers={"X-Principal": "ceo"}).json()
        agent_items = [i for i in items if i["kind"] == "proposal"]
        assert agent_items, "the agent's proposals never reached the queue"
        assert all(i["proposed_by"] == "agent-seeder" for i in agent_items)
        assert all(i["delegated_by"] == "ceo" for i in agent_items)

    def test_fifty_decisions_over_http_only(self, client: TestClient) -> None:
        headers = {"X-Principal": "ceo"}
        queued = client.get("/api/review?limit=200", headers=headers).json()[:BATCH]
        assert len(queued) == BATCH
        edges = [i["key"] for i in queued if i["kind"] == "edge"]
        proposals = [i["key"] for i in queued if i["kind"] == "proposal"]
        assert edges and proposals, "the batch should contain both kinds"

        started = time.monotonic()
        # One at a time for the agent proposals — each is a distinct claim a
        # reviewer reads — and one bulk call for the edges, which is what
        # recognising a pattern looks like.
        for key in proposals:
            response = client.post(
                "/api/review/decide",
                headers=headers,
                json={"items": [{"key": key, "kind": "proposal"}], "decision": "accepted"},
            )
            assert response.status_code == 200, response.text
        bulk = client.post(
            "/api/review/decide",
            headers=headers,
            json={"items": [{"key": k, "kind": "edge"} for k in edges], "decision": "rejected"},
        )
        assert bulk.status_code == 200, bulk.text
        assert bulk.json()["decided"] == len(edges)
        elapsed = time.monotonic() - started

        assert elapsed < MACHINE_BUDGET_SECONDS, (
            f"{BATCH} decisions cost {elapsed:.1f}s of machine time out of a "
            f"15-minute human budget"
        )

        remaining = {
            i["key"] for i in client.get("/api/review?limit=200", headers=headers).json()
        }
        assert not (set(edges) | set(proposals)) & remaining

    def test_every_decision_carries_the_reviewers_name(self, client: TestClient) -> None:
        headers = {"X-Principal": "support-lead"}
        key = next(
            i["key"]
            for i in client.get("/api/review?limit=50", headers=headers).json()
            if i["kind"] == "edge"
        )
        response = client.post(
            "/api/review/decide",
            headers=headers,
            json={"items": [{"key": key, "kind": "edge"}], "decision": "accepted"},
        )
        assert response.json()["by"] == "support-lead"

        trail = client.get("/api/audit?limit=10", headers=headers).json()
        assert trail[0]["actor"] == "support-lead"
        assert trail[0]["action"] == "review.accept"

    def test_the_decision_is_not_taken_from_the_request_body(self, client: TestClient) -> None:
        """Invariant 8's shape, on the reviewer side. Identity is out-of-band
        even here — a body field naming the reviewer would be a body field
        naming anyone."""
        key = next(
            i["key"]
            for i in client.get("/api/review?limit=50", headers={"X-Principal": "ceo"}).json()
            if i["kind"] == "edge"
        )
        response = client.post(
            "/api/review/decide",
            headers={"X-Principal": "eng-ic"},
            json={
                "items": [{"key": key, "kind": "edge"}],
                "decision": "accepted",
                "reviewer": "ceo",
            },
        )
        assert response.json()["by"] == "eng-ic"

    def test_gate_telemetry_is_available_to_the_reviewer(self, client: TestClient) -> None:
        """§11's calibration signal, surfaced rather than buried in a metric:
        near 100% means the gate is theatre, near 10% means the extractor is
        wasting the reviewer's time."""
        headers = {"X-Principal": "ceo"}
        keys = [
            i["key"]
            for i in client.get("/api/review?limit=200", headers=headers).json()
            if i["kind"] == "edge"
        ][:10]
        client.post(
            "/api/review/decide",
            headers=headers,
            json={"items": [{"key": k, "kind": "edge"} for k in keys], "decision": "accepted"},
        )

        stats = client.get("/api/review/stats", headers=headers).json()
        assert stats["accept_rate"], "no calibration signal after ten decisions"
        assert all(decided >= accepted for accepted, decided in stats["accept_rate"].values())
        assert set(stats) >= {"pending", "pending_proposals", "by_predicate"}
