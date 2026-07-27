"""The audit log.

"Who saw what, when" is an M5 requirement. It is tested now because it is the
one requirement that cannot be added later: an audit log introduced in M5 has
nothing to say about anything that happened before it, and backfilling is not a
thing you can do to a record of the past.

The property under test throughout is invariant 15 — node IDs, never content.
An audit log that quietly accumulates document text is a second copy of the
corpus with none of the ACL machinery around it, sitting in a file that
operators are encouraged to read.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from company_brain.audit.log import (
    Action,
    AuditError,
    AuditLog,
    AuditRecord,
    Outcome,
    Surface,
    summarize,
)
from company_brain.schemas.acl import Principal, PrincipalKind
from company_brain.store.backend import MemoryBackend


class Clock:
    def __init__(self) -> None:
        self.tick = 0

    def __call__(self) -> datetime:
        self.tick += 1
        return datetime(2026, 3, 1, 9, 0, 0, self.tick, tzinfo=UTC)


@pytest.fixture
def log() -> AuditLog:
    return AuditLog(MemoryBackend(), surface=Surface.MCP, clock=Clock())


def agent(name: str = "agent-x", human: str = "ceo") -> Principal:
    return Principal(id=name, kind=PrincipalKind.AGENT, display=name, delegated_by=human)


class TestContentNeverEntersTheLog:
    def test_node_ids_must_be_node_ids(self, log: AuditLog) -> None:
        """The field a careless caller reaches for to log "context"."""
        with pytest.raises(AuditError):
            log.record(
                actor="ceo",
                action=Action.READ_NODE,
                outcome=Outcome.OK,
                node_ids=["Sam said the renewal is at risk"],
            )

    def test_an_unknown_type_segment_is_refused(self, log: AuditLog) -> None:
        with pytest.raises(AuditError):
            log.record(
                actor="ceo",
                action=Action.READ_NODE,
                outcome=Outcome.OK,
                node_ids=["secrets/comp-plan"],
            )

    def test_detail_is_one_short_line(self, log: AuditLog) -> None:
        """Not a rule of taste. A `detail` that can hold a paragraph will
        eventually hold a document."""
        record = log.record(
            actor="ceo",
            action=Action.WRITE_NODE,
            outcome=Outcome.REFUSED,
            detail="line one\nline two\n" + "x" * 500,
        )
        assert "\n" not in record.detail
        assert len(record.detail) <= 160

    def test_a_refused_write_does_not_log_the_body(self) -> None:
        """The end-to-end version: propose a body, then grep the whole log for
        it. This is the assertion that catches a well-meaning `detail=body[:50]`
        added six months from now."""
        from tests.unit.test_agent_writes import Harness, node

        secret = "Acquisition of Northwind closes in April"
        harness = Harness([node("people/sam-kaur")])
        harness.tools.write_node("people/sam-kaur", {"body": f"{secret}\n"})

        serialized = "\n".join(str(r.to_dict()) for r in harness.audit.scan())
        assert secret not in serialized
        assert "people/sam-kaur" in serialized


class TestTheRecordShape:
    def test_an_agent_record_names_both_identities(self, log: AuditLog) -> None:
        """§8.2. "The research agent read the comp thread" and "the CEO's
        research agent read the comp thread" are different facts, and only the
        second one is true."""
        record = log.record(
            actor=agent(),
            action=Action.READ_NODE,
            outcome=Outcome.OK,
            node_ids=["documents/comp-plan-abc123"],
        )
        assert record.actor == "agent-x"
        assert record.delegated_by == "ceo"

    def test_a_human_record_has_no_delegation(self, log: AuditLog) -> None:
        human = Principal(id="ceo", kind=PrincipalKind.USER, display="Chief")
        assert (
            log.record(
                actor=human, action=Action.REVIEW_ACCEPT, outcome=Outcome.OK
            ).delegated_by
            is None
        )

    def test_records_round_trip(self, log: AuditLog) -> None:
        written = log.record(
            actor=agent(),
            action=Action.PROPOSE_EDGE,
            outcome=Outcome.OK,
            node_ids=["people/sam-kaur", "processes/vendor-renewals"],
            proposal_id="edge-agent-x-deadbeef",
            detail="owns",
        )
        (read_back,) = list(log.scan())
        assert read_back == written
        assert AuditRecord.from_dict(written.to_dict()) == written


class TestOrderingAndQuery:
    def test_scan_is_chronological(self, log: AuditLog) -> None:
        """Filenames lead with a fixed-width UTC stamp, so sorted-by-name is
        sorted-by-time and `walk` needs no second pass."""
        for i in range(5):
            log.record(actor=f"a{i}", action=Action.SEARCH, outcome=Outcome.OK)
        assert [r.actor for r in log.scan()] == ["a0", "a1", "a2", "a3", "a4"]

    def test_read_is_most_recent_first(self, log: AuditLog) -> None:
        """The order an incident is investigated in."""
        for i in range(5):
            log.record(actor=f"a{i}", action=Action.SEARCH, outcome=Outcome.OK)
        assert [r.actor for r in log.read(limit=2)] == ["a4", "a3"]

    def test_filtering_by_node_answers_who_saw_this(self, log: AuditLog) -> None:
        log.record(
            actor="ceo",
            action=Action.READ_NODE,
            outcome=Outcome.OK,
            node_ids=["documents/comp-plan-abc123"],
        )
        log.record(
            actor=agent(),
            action=Action.SEARCH,
            outcome=Outcome.OK,
            node_ids=["documents/comp-plan-abc123", "people/sam-kaur"],
        )
        log.record(
            actor="contractor",
            action=Action.SEARCH,
            outcome=Outcome.OK,
            node_ids=["people/sam-kaur"],
        )

        saw = {r.actor for r in log.read(node_id="documents/comp-plan-abc123")}
        assert saw == {"ceo", "agent-x"}

    def test_an_identical_record_does_not_duplicate(self, log: AuditLog) -> None:
        """Content-addressed filenames make a retried write idempotent rather
        than a second event that never happened."""
        stamped = datetime(2026, 3, 1, 9, 0, tzinfo=UTC)
        fixed = AuditLog(log.backend, surface=Surface.API, clock=lambda: stamped)
        for _ in range(3):
            fixed.record(actor="ceo", action=Action.SEARCH, outcome=Outcome.OK)
        assert fixed.count() == 1

    def test_summarize_counts_action_and_outcome_together(self, log: AuditLog) -> None:
        """A refused write and a successful one are not the same event, and a
        tally that merges them hides exactly the thing an operator is looking
        for."""
        log.record(actor="a", action=Action.WRITE_NODE, outcome=Outcome.OK)
        log.record(actor="a", action=Action.WRITE_NODE, outcome=Outcome.REFUSED)
        log.record(actor="b", action=Action.WRITE_NODE, outcome=Outcome.REFUSED)
        assert summarize(log.scan()) == {
            "write_node:ok": 1,
            "write_node:refused": 2,
        }


class TestSurfaceIsBoundNotPassed:
    def test_the_surface_comes_from_the_log_not_the_caller(self) -> None:
        """A caller that can name its own surface per call can claim to be a
        different one."""
        import inspect

        params = inspect.signature(AuditLog.record).parameters
        assert "surface" not in params
        assert (
            inspect.signature(AuditLog.__init__).parameters["surface"].kind
            is inspect.Parameter.KEYWORD_ONLY
        )

    def test_each_surface_writes_to_the_same_store(self) -> None:
        backend = MemoryBackend()
        clock = Clock()
        AuditLog(backend, surface=Surface.MCP, clock=clock).record(
            actor="agent-x", action=Action.SEARCH, outcome=Outcome.OK
        )
        AuditLog(backend, surface=Surface.API, clock=clock).record(
            actor="ceo", action=Action.REVIEW_ACCEPT, outcome=Outcome.OK
        )
        reader = AuditLog(backend, surface=Surface.CLI, clock=clock)
        assert {str(r.surface) for r in reader.scan()} == {"mcp", "api"}
