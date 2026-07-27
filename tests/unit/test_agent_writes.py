"""The agent write path: proposals, blocks, and the audit trail.

The three ROADMAP M3 acceptance criteria this file is responsible for:

* a direct graph write from an agent is rejected **and audited**;
* an ACL-widening attempt is **blocked rather than queued**;
* a reviewer can clear the queue without a terminal — which here means the
  operations the UI calls have to exist, batch, and be undoable.

The distinction the tests keep returning to is *blocked* versus *queued*. A
queued widening is a widening that a tired human can approve, so §11's last row
does not say "propose"; it says hard block. Every widening test below therefore
asserts two things: that the call raised, and that nothing landed in the queue.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from company_brain.acl.grants import GrantTable
from company_brain.audit.log import Action, AuditLog, Outcome, Surface
from company_brain.index.base import IndexedNode
from company_brain.index.memory import MemoryIndex
from company_brain.mcp.guard import (
    AclWideningBlocked,
    AgentWriteRefused,
    PatchFieldRefused,
)
from company_brain.mcp.server import McpTools, Session, SessionNotAuthorized
from company_brain.normalize.formats import default_registry
from company_brain.review.proposals import ProposalState, ProposalStore
from company_brain.review.queue import Decision, ReviewQueue
from company_brain.schemas.acl import AclRef, Principal, PrincipalKind, Sensitivity
from company_brain.schemas.edges import Edge, EdgeStatus, Evidence, Predicate, Provenance
from company_brain.schemas.nodes import Frontmatter, Node, NodeType
from company_brain.store.backend import MemoryBackend
from company_brain.store.fences import render_fence
from company_brain.store.repository import Repository

INTERNAL = Sensitivity.INTERNAL
RESTRICTED = Sensitivity.RESTRICTED

OPEN_REF = "slack:channel:OPEN"
VAULT_REF = "slack:channel:VAULT"


def node(
    node_id: str,
    *,
    ref: str = OPEN_REF,
    tier: Sensitivity = INTERNAL,
    title: str = "A page",
    body: str = "Original body.\n",
    relations: tuple[Edge, ...] = (),
) -> Node:
    node_type = NodeType.PROCESS if node_id.startswith("processes/") else NodeType.PERSON
    return Node(
        frontmatter=Frontmatter(
            id=node_id,
            type=node_type,
            title=title,
            acl=AclRef(ref=ref, sensitivity=tier),
            relations=relations,
        ),
        body=body,
    )


class Clock:
    """A pinned clock. An audit log whose time a test cannot control is an audit
    log whose ordering a test cannot assert on."""

    def __init__(self) -> None:
        self.tick = 0

    def __call__(self) -> datetime:
        self.tick += 1
        return datetime(2026, 3, 1, 12, 0, self.tick % 60, self.tick, tzinfo=UTC)


class Harness:
    """A store, an index, grants, and a bound session over all three."""

    def __init__(self, nodes: list[Node], *, read_only: bool = False) -> None:
        from company_brain.app import App, Providers
        from company_brain.extract.rules import Roster, RuleBasedExtractor
        from company_brain.index.base import HashingEmbedder

        self.backend = MemoryBackend()
        self.repo = Repository(self.backend)
        for item in nodes:
            self.repo.put(item)

        self.index = MemoryIndex()
        self.index.rebuild(
            [
                (
                    IndexedNode(
                        id=n.id,
                        type=str(n.frontmatter.type),
                        title=n.frontmatter.title,
                        acl_ref=n.frontmatter.acl.ref,
                        sensitivity=n.frontmatter.acl.sensitivity,
                        status="active",
                        content_sha256="",
                        edges=n.frontmatter.relations,
                    ),
                    n.body,
                )
                for n in nodes
            ]
        )

        self.grants = GrantTable()
        self.grants.grant("boss", OPEN_REF, INTERNAL)
        self.grants.grant("boss", VAULT_REF, RESTRICTED)
        self.grants.grant("staff", OPEN_REF, INTERNAL)

        roster = Roster()
        self.app = App(
            repo=self.repo,
            registry=default_registry(),
            grants=self.grants,
            index=self.index,
            providers=Providers(
                extractor=RuleBasedExtractor(roster),
                embedder=HashingEmbedder(),
                synthesizer_name="extractive-offline",
                offline=True,
                reason="test",
            ),
        )
        self.clock = Clock()
        self.audit = AuditLog(self.backend, surface=Surface.MCP, clock=self.clock)
        self.session = Session.bind(
            self.app,
            agent_id="agent-x",
            delegated_by="boss",
            read_only=read_only,
            audit=self.audit,
        )
        self.tools = McpTools(self.session)
        self.proposals = ProposalStore(self.repo)

    def pending(self) -> list[str]:
        return [r.proposal_id for r in self.proposals.records(state=ProposalState.PENDING)]

    def audited(self, action: Action) -> list[object]:
        return [r for r in self.audit.scan() if r.action is action]


@pytest.fixture
def harness() -> Harness:
    return Harness(
        [
            node("processes/vendor-renewals", title="Vendor renewals"),
            node("people/sam-kaur", title="Sam Kaur"),
            node("people/dev-oyelaran", title="Dev Oyelaran", ref=VAULT_REF, tier=RESTRICTED),
        ]
    )


class TestDirectWritesAreRefused:
    """Invariant 9, made testable.

    It used to hold by absence — no tool called `repo.put`, so nothing could.
    Absence is a real defence and an untestable one: it produces no evidence
    when someone tries, and it degrades the moment a sixth tool is written by
    someone who has not read the file.
    """

    def test_put_is_refused_and_audited(self, harness: Harness) -> None:
        with pytest.raises(AgentWriteRefused):
            harness.session.store.put(node("people/sam-kaur", body="rewritten"))

        records = harness.audited(Action.GRAPH_WRITE_REFUSED)
        assert len(records) == 1
        assert records[0].outcome is Outcome.REFUSED  # type: ignore[attr-defined]
        assert records[0].actor == "agent-x"  # type: ignore[attr-defined]
        assert records[0].delegated_by == "boss"  # type: ignore[attr-defined]

    def test_the_graph_is_untouched_by_a_refused_write(self, harness: Harness) -> None:
        with pytest.raises(AgentWriteRefused):
            harness.session.store.put(node("people/sam-kaur", body="rewritten"))
        assert harness.repo.get("people/sam-kaur").body.strip() == "Original body."

    @pytest.mark.parametrize(
        ("operation", "args"),
        [
            ("tombstone", ("people/sam-kaur",)),
            ("redirect", ("people/sam-kaur", "people/other")),
            ("put_proposal", ("id", None)),
        ],
    )
    def test_every_mutator_is_walled(
        self, harness: Harness, operation: str, args: tuple[object, ...]
    ) -> None:
        """Including `put_proposal`, which writes to `_proposals/`.

        It is refused because it skips the ACL inheritance check and the queue
        row — it would produce an unreviewable proposal that no widening check
        ever saw, which is worse than no proposal at all.
        """
        with pytest.raises(AgentWriteRefused):
            getattr(harness.session.store, operation)(*args)
        assert harness.audited(Action.GRAPH_WRITE_REFUSED)

    def test_tools_never_reach_the_real_repository(self) -> None:
        """A structural guard, so the wall cannot be walked around by a new tool."""
        import ast
        import inspect

        from company_brain.mcp import server

        tree = ast.parse(inspect.getsource(server.McpTools))
        for element in ast.walk(tree):
            if not isinstance(element, ast.Attribute) or element.attr != "repo":
                continue
            # `self.session.app.repo` is the Repository itself. Tools get
            # `self.session.store`, which is the ProposalOnlyStore.
            source = ast.unparse(element)
            raise AssertionError(f"McpTools reaches the raw repository via {source}")


class TestAclWideningIsBlockedNotQueued:
    def test_patching_acl_is_blocked(self, harness: Harness) -> None:
        with pytest.raises(AclWideningBlocked):
            harness.tools.write_node(
                "people/sam-kaur", {"acl": {"ref": OPEN_REF, "sensitivity": "public"}}
            )
        assert harness.pending() == [], "a widening attempt was queued for review"
        assert harness.audited(Action.ACL_WIDENING_BLOCKED)

    def test_an_edge_to_a_restricted_node_is_blocked(self, harness: Harness) -> None:
        """The subtle one, and the reason `inherited_tier` takes both ends.

        No restricted *prose* moves. But an internal node asserting a relation
        to a restricted node publishes that node's existence and ID to everyone
        holding the internal grant, and the assertion would be readable at
        internal tier forever after.
        """
        with pytest.raises(AclWideningBlocked):
            harness.tools.propose_edge(
                "processes/vendor-renewals",
                "owns",
                "people/dev-oyelaran",
                "Dev signs the renewals.",
            )
        assert harness.pending() == []
        blocked = harness.audited(Action.ACL_WIDENING_BLOCKED)
        assert blocked and blocked[0].outcome is Outcome.BLOCKED  # type: ignore[attr-defined]

    def test_the_same_edge_within_one_tier_is_allowed(self, harness: Harness) -> None:
        """The control. If this failed, the block above would just be "edges
        don't work" wearing a security costume."""
        result = harness.tools.propose_edge(
            "processes/vendor-renewals",
            "owns",
            "people/sam-kaur",
            "Sam signs the renewals.",
        )
        assert result["state"] == "pending_review"
        assert harness.pending() == [result["proposal_id"]]

    def test_an_unpatchable_field_is_refused_not_ignored(self, harness: Harness) -> None:
        """Silently dropping an unknown key is the worst option: the agent
        believes it succeeded and no one finds out until the graph is wrong."""
        with pytest.raises(PatchFieldRefused):
            harness.tools.write_node("people/sam-kaur", {"status": "deleted"})
        assert harness.pending() == []
        assert harness.audited(Action.PATCH_FIELD_REFUSED)

    def test_a_proposal_carries_the_nodes_own_acl(self, harness: Harness) -> None:
        result = harness.tools.write_node("people/sam-kaur", {"body": "Sam leads finance.\n"})
        proposed = harness.proposals.get_node(result["proposal_id"])
        original = harness.repo.get("people/sam-kaur")
        assert proposed.frontmatter.acl == original.frontmatter.acl

    def test_a_generated_region_may_not_be_touched(self) -> None:
        """Invariant 13 for the agent path. An accepted proposal is a write, and
        a machine's write may not land on human-facing text by rewriting the
        fence it does not own."""
        body = "Human notes.\n\n" + render_fence("relations", "- owns processes/x") + "\n"
        harness = Harness([node("people/sam-kaur", body=body)])
        with pytest.raises(AgentWriteRefused, match="generated region"):
            harness.tools.write_node("people/sam-kaur", {"body": "Human notes.\n"})
        assert harness.pending() == []

    def test_editing_around_a_fence_is_fine(self) -> None:
        fence = render_fence("relations", "- owns processes/x")
        harness = Harness([node("people/sam-kaur", body=f"Human notes.\n\n{fence}\n")])
        result = harness.tools.write_node(
            "people/sam-kaur", {"body": f"Human notes.\nAlso: on leave.\n\n{fence}\n"}
        )
        assert result["state"] == "pending_review"


class TestDelegatedIdentity:
    """Invariant 8 on the write path.

    Reads have been intersected since M1. The question a write raises is whether
    an agent can *propose against* something its human cannot see — which would
    be an existence oracle, and was the hole in the first version of
    `write_node`: it went straight to `repo.find`, which does no ACL check at
    all.
    """

    def test_an_agent_cannot_propose_against_an_invisible_node(self) -> None:
        harness = Harness(
            [node("people/dev-oyelaran", ref=VAULT_REF, tier=RESTRICTED)],
        )
        harness.session = Session.bind(
            harness.app,
            agent_id="agent-x",
            delegated_by="staff",  # staff holds OPEN only
            audit=harness.audit,
        )
        harness.tools = McpTools(harness.session)

        with pytest.raises(KeyError):
            harness.tools.write_node("people/dev-oyelaran", {"body": "nope"})
        assert harness.pending() == []

    def test_not_found_and_not_visible_are_indistinguishable(self) -> None:
        """§6.3. The two must fail the same way, or `write_node` becomes a probe
        for the existence of restricted content."""
        harness = Harness([node("people/dev-oyelaran", ref=VAULT_REF, tier=RESTRICTED)])
        harness.session = Session.bind(
            harness.app, agent_id="a", delegated_by="staff", audit=harness.audit
        )
        tools = McpTools(harness.session)

        def attempt(node_id: str) -> tuple[type[BaseException], str]:
            try:
                tools.write_node(node_id, {"body": "x"})
            except BaseException as exc:
                return type(exc), str(exc)
            raise AssertionError(f"{node_id} did not fail")

        invisible_type, invisible_message = attempt("people/dev-oyelaran")
        absent_type, absent_message = attempt("people/nobody-at-all")

        assert invisible_type is absent_type is KeyError
        # And the messages differ only by the ID the caller already supplied.
        assert invisible_message.replace("dev-oyelaran", "nobody-at-all") == absent_message

    def test_a_proposal_records_both_identities(self, harness: Harness) -> None:
        result = harness.tools.write_node("people/sam-kaur", {"body": "New text.\n"})
        record = harness.proposals.get_record(result["proposal_id"])
        assert record.proposed_by == "agent-x"
        assert record.delegated_by == "boss"

    def test_binding_to_an_ungranted_human_fails_loudly(self, harness: Harness) -> None:
        with pytest.raises(SessionNotAuthorized):
            Session.bind(
                harness.app, agent_id="a", delegated_by="who-even", audit=harness.audit
            )

    def test_a_read_only_session_cannot_propose(self) -> None:
        harness = Harness([node("people/sam-kaur")], read_only=True)
        with pytest.raises(AgentWriteRefused, match="read-only"):
            harness.tools.write_node("people/sam-kaur", {"body": "New text.\n"})
        assert harness.pending() == []

    def test_no_tool_takes_a_principal(self) -> None:
        import inspect

        forbidden = {"principal", "principal_id", "user", "user_id", "as_user", "acl"}
        for name, method in inspect.getmembers(McpTools, inspect.isfunction):
            if name.startswith("_"):
                continue
            params = set(inspect.signature(method).parameters) - {"self"}
            assert not (params & forbidden), f"{name} accepts identity"


class TestProposalsAreInertUntilAccepted:
    def test_a_proposal_does_not_change_the_graph(self, harness: Harness) -> None:
        harness.tools.propose_edge(
            "processes/vendor-renewals", "owns", "people/sam-kaur", "Sam signs."
        )
        assert harness.repo.get("processes/vendor-renewals").frontmatter.relations == ()

    def test_re_proposing_the_same_change_is_one_queue_entry(self, harness: Harness) -> None:
        """Content-addressed IDs. A queue that double-counts a retry is a queue
        whose depth means nothing."""
        first = harness.tools.write_node("people/sam-kaur", {"body": "Same text.\n"})
        second = harness.tools.write_node("people/sam-kaur", {"body": "Same text.\n"})
        assert first["proposal_id"] == second["proposal_id"]
        assert len(harness.pending()) == 1

    def test_two_agents_proposing_the_same_thing_are_two_entries(
        self, harness: Harness
    ) -> None:
        """Corroboration is signal. Collapsing it would hide that two
        independent readers reached the same conclusion."""
        other = Session.bind(
            harness.app, agent_id="agent-y", delegated_by="boss", audit=harness.audit
        )
        harness.tools.write_node("people/sam-kaur", {"body": "Same text.\n"})
        McpTools(other).write_node("people/sam-kaur", {"body": "Same text.\n"})
        assert len(harness.pending()) == 2

    def test_accepting_a_proposal_writes_it_under_the_reviewers_name(
        self, harness: Harness
    ) -> None:
        result = harness.tools.propose_edge(
            "processes/vendor-renewals", "owns", "people/sam-kaur", "Sam signs."
        )
        queue = ReviewQueue(harness.repo, audit=harness.audit)
        reviewer = Principal(id="boss", kind=PrincipalKind.USER, display="The Boss")
        queue.decide_proposal(result["proposal_id"], Decision.ACCEPTED, reviewer=reviewer)

        relations = harness.repo.get("processes/vendor-renewals").frontmatter.relations
        assert [str(e.predicate) for e in relations] == ["owns"]
        # Still proposed as an *edge*: a human accepting the proposal agreed the
        # claim was worth recording, not that the gate should be skipped.
        assert relations[0].status is EdgeStatus.PROPOSED

        record = harness.proposals.get_record(result["proposal_id"])
        assert record.state is ProposalState.ACCEPTED
        assert record.decided_by == "boss"
        assert harness.audited(Action.PROPOSAL_APPLY)

    def test_a_rejected_proposal_is_retained(self, harness: Harness) -> None:
        result = harness.tools.write_node("people/sam-kaur", {"body": "New text.\n"})
        queue = ReviewQueue(harness.repo, audit=harness.audit)
        queue.decide_proposal(result["proposal_id"], Decision.REJECTED, reviewer="boss")

        record = harness.proposals.get_record(result["proposal_id"])
        assert record.state is ProposalState.REJECTED
        # The markdown is still there to diff against, and still counted.
        assert harness.proposals.get_node(result["proposal_id"]).body.strip() == "New text."
        assert harness.proposals.accept_rate()["node_body"] == (0, 1)

    def test_accepting_one_edge_proposal_does_not_strand_the_others(
        self, harness: Harness
    ) -> None:
        """Ten proposals against one document is the normal case.

        Accepting the first moves the document, so replaying the second one's
        whole node would drop the first one's edge — the queue stalling on its
        own success. An edge proposal claims one relation, so it is rebased onto
        the node as it stands.
        """
        first = harness.tools.propose_edge(
            "processes/vendor-renewals", "owns", "people/sam-kaur", "Sam signs."
        )
        second = harness.tools.propose_edge(
            "processes/vendor-renewals", "mentions", "people/sam-kaur", "Sam is named."
        )
        queue = ReviewQueue(harness.repo, audit=harness.audit)
        queue.decide_proposal(first["proposal_id"], Decision.ACCEPTED, reviewer="boss")
        queue.decide_proposal(second["proposal_id"], Decision.ACCEPTED, reviewer="boss")

        relations = harness.repo.get("processes/vendor-renewals").frontmatter.relations
        assert {str(e.predicate) for e in relations} == {"owns", "mentions"}

    def test_the_diff_describes_the_change_against_the_current_node(
        self, harness: Harness
    ) -> None:
        """Not against the proposal's base. The reviewer approves the change
        that will actually happen."""
        result = harness.tools.propose_edge(
            "processes/vendor-renewals", "owns", "people/sam-kaur", "Sam signs."
        )
        diff = harness.proposals.diff(result["proposal_id"])
        assert [str(e.predicate) for e in diff.added_relations] == ["owns"]
        assert diff.removed_relations == ()
        assert diff.body == (), "an edge proposal must not claim a body change"
        assert not diff.stale

    def test_a_rejected_proposal_can_be_reopened_but_an_accepted_one_cannot(
        self, harness: Harness
    ) -> None:
        """The asymmetry is real, not an omission.

        Rejecting changes only the queue row, so putting it back is a complete
        undo. Accepting wrote to the graph, and un-writing a node is a second
        write a reviewer has to see — so it refuses and points at the edge.
        """
        from company_brain.review.proposals import ProposalError

        queue = ReviewQueue(harness.repo, audit=harness.audit)
        rejected = harness.tools.write_node("people/sam-kaur", {"body": "One.\n"})
        accepted = harness.tools.propose_edge(
            "processes/vendor-renewals", "owns", "people/sam-kaur", "Sam signs."
        )
        queue.decide_proposal(rejected["proposal_id"], Decision.REJECTED, reviewer="boss")
        queue.decide_proposal(accepted["proposal_id"], Decision.ACCEPTED, reviewer="boss")

        queue.decide_proposal(rejected["proposal_id"], Decision.PENDING, reviewer="boss")
        assert rejected["proposal_id"] in harness.pending()

        with pytest.raises(ProposalError, match="already in the graph"):
            queue.decide_proposal(accepted["proposal_id"], Decision.PENDING, reviewer="boss")

    def test_a_stale_body_proposal_cannot_be_accepted(self, harness: Harness) -> None:
        """The other half of the rebase rule.

        An edge proposal rebases, because "add this relation" is well defined
        against a moved node. A body proposal cannot: rebasing prose means a
        three-way merge, and a merge nobody reviewed is exactly the silent
        revert a review step exists to prevent. So staleness stays fatal here,
        and the reviewer is told to re-propose.
        """
        from company_brain.review.proposals import StaleProposalError

        result = harness.tools.write_node("people/sam-kaur", {"body": "Agent text.\n"})
        harness.repo.put(node("people/sam-kaur", body="A human got there first.\n"))

        queue = ReviewQueue(harness.repo, audit=harness.audit)
        with pytest.raises(StaleProposalError):
            queue.decide_proposal(result["proposal_id"], Decision.ACCEPTED, reviewer="boss")
        assert harness.repo.get("people/sam-kaur").body.strip() == "A human got there first."


class TestReviewerThroughput:
    """The 50-in-15-minutes criterion, expressed as the operations it needs.

    Eighteen seconds per item buys reading the evidence and one keystroke. It
    does not buy re-confirming a pattern fifty times, and it does not buy
    reverting a misclick by hand-editing markdown — so bulk and undo are
    correctness requirements here, not conveniences.
    """

    @pytest.fixture
    def loaded(self) -> Harness:
        edges = tuple(
            Edge(
                predicate=Predicate.MENTIONS,
                object=f"people/person-{i}",
                confidence=0.7,
                provenance=Provenance.LLM,
                status=EdgeStatus.PROPOSED,
                evidence=(Evidence(quote=f"mention {i}"),),
            )
            for i in range(25)
        )
        return Harness(
            [
                node("processes/vendor-renewals", relations=edges),
                *[node(f"people/person-{i}") for i in range(25)],
            ]
        )

    def test_a_bulk_decision_is_one_write_per_node(self, loaded: Harness) -> None:
        queue = ReviewQueue(loaded.repo, audit=loaded.audit)
        keys = [item.key for item in queue.pending_edges()]
        assert len(keys) == 25

        written = queue.decide_many(keys, Decision.ACCEPTED, reviewer="boss")
        assert len(written) == 1, "25 edges on one node should cost one store write"
        assert queue.pending_edges() == []

    def test_a_partial_bulk_decision_writes_nothing(self, loaded: Harness) -> None:
        """Half-applied is worse than refused: the reviewer cannot tell which
        half landed, and the queue no longer describes the graph."""
        queue = ReviewQueue(loaded.repo, audit=loaded.audit)
        keys = [item.key for item in queue.pending_edges()]
        with pytest.raises(KeyError):
            queue.decide_many(
                [*keys, "processes/vendor-renewals||owns|people/ghost"],
                Decision.ACCEPTED,
                reviewer="boss",
            )
        assert len(queue.pending_edges()) == 25

    def test_a_decision_can_be_undone(self, loaded: Harness) -> None:
        queue = ReviewQueue(loaded.repo, audit=loaded.audit)
        key = queue.pending_edges()[0].key

        queue.decide(key, Decision.REJECTED, reviewer="boss")
        assert key not in [i.key for i in queue.pending_edges()]

        queue.decide(key, Decision.PENDING, reviewer="boss")
        assert key in [i.key for i in queue.pending_edges()]
        assert loaded.audited(Action.REVIEW_REOPEN)

    def test_reopening_something_pending_is_an_error(self, loaded: Harness) -> None:
        queue = ReviewQueue(loaded.repo, audit=loaded.audit)
        key = queue.pending_edges()[0].key
        with pytest.raises(ValueError, match="already pending"):
            queue.decide(key, Decision.PENDING, reviewer="boss")

    def test_every_decision_names_a_reviewer(self, loaded: Harness) -> None:
        """No default, at the signature level: a graph write with no name on it
        cannot answer the M5 question, and that question is asked about M3's
        decisions."""
        import inspect

        for name in ("decide", "decide_many", "decide_proposal"):
            signature = inspect.signature(getattr(ReviewQueue, name))
            reviewer = signature.parameters["reviewer"]
            assert reviewer.default is inspect.Parameter.empty
            assert reviewer.kind is inspect.Parameter.KEYWORD_ONLY

    def test_the_accept_rate_survives_a_bulk_pass(self, loaded: Harness) -> None:
        """The §11 calibration signal has to keep working when the reviewer uses
        the fast path, or the fast path quietly destroys the metric that says
        whether the gate was worth having."""
        queue = ReviewQueue(loaded.repo, audit=loaded.audit)
        keys = [item.key for item in queue.pending_edges()]
        queue.decide_many(keys[:20], Decision.ACCEPTED, reviewer="boss")
        queue.decide_many(keys[20:], Decision.REJECTED, reviewer="boss")
        assert queue.accept_rate()["mentions"] == (20, 25)
