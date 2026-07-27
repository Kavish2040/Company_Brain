"""Outreach: the permission boundary, the state machine, and the audit trail.

Outreach is the only path in this system that ends with a message addressed to
a real person, which makes it the only one where a permissions bug is not a
disclosure to a logged-in colleague but a disclosure to the outside. Three
properties carry that weight and are asserted here rather than assumed:

1. **A principal who cannot see a node cannot draft from it**, and is told
   "not found" rather than "forbidden" — the same answer `get_node` gives, so
   the endpoint does not become an oracle for which nodes exist.
2. **Restricted content is refused even from a principal who holds it.** The
   grant is not the question; an outbound message composed from restricted
   material is an exfiltration path, and the path is closed rather than
   guarded.
3. **Only an approved draft can be sent, once.** Every other state, and every
   replay, is refused — and each refusal is auditable.

The corpus is generated and ingested once for the module, because the ACL
shape being tested is the corpus's own: `people/*` are internal, the planted
comp channel is restricted, and the contractor holds only the public channel.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from company_brain.app import build_app, cached_extractor
from company_brain.audit.log import Action, Outcome, Surface
from company_brain.connectors.local_fs import LocalIngest
from company_brain.corpus.generate import generate
from company_brain.outreach.apollo import (
    ApolloClient,
    ApolloError,
    Lead,
    OfflineLeadSource,
    choose_lead_source,
)
from company_brain.outreach.drafts import (
    OutreachDraft,
    OutreachError,
    OutreachState,
    OutreachStore,
    compose,
    draft_id,
)
from company_brain.schemas.acl import Sensitivity

CEO = {"X-Principal": "ceo"}
CONTRACTOR = {"X-Principal": "contractor"}
# A Person node. Internal, so the CEO and eng-ic reach it and the contractor
# — who holds only the public channel — does not.
PERSON = "people/ana-brito"


@pytest.fixture(scope="module")
def store(tmp_path_factory: pytest.TempPathFactory) -> Path:
    base = tmp_path_factory.mktemp("outreach")
    corpus, store_root = base / "corpus", base / "store"
    generate(corpus)
    app = build_app(store_root)
    ingest = LocalIngest(
        app.repo, app.registry, cached_extractor(app, store_root, frozen=False)
    )
    ingest.run(corpus)
    return store_root


@pytest.fixture
def client(store: Path) -> Iterator[TestClient]:
    from company_brain.api.app import _app, api, get_app

    # Draft ids are content-addressed on (node, author, body), so every test
    # drafting for the same person as the same principal produces the *same*
    # id — and a draft this module already sent would refuse to be re-drafted.
    # That refusal is the product working (see
    # `test_a_decided_draft_cannot_be_redrafted_into_pending`), so the fix is
    # per-test isolation rather than a weaker guard. Only the sidecars reset;
    # the ingested corpus stays module-scoped because it is what costs.
    shutil.rmtree(store / "_outreach", ignore_errors=True)

    instance = build_app(store)
    instance.load_index()
    api.dependency_overrides[get_app] = lambda: instance
    with TestClient(api) as test_client:
        yield test_client
    api.dependency_overrides.clear()
    _app.cache_clear()


def a_restricted_node(store: Path) -> str:
    app = build_app(store)
    for node in app.repo.walk():
        if node.frontmatter.acl.sensitivity is Sensitivity.RESTRICTED:
            return node.id
    pytest.skip("the corpus has no restricted node")


class TestDraftPermissions:
    def test_a_principal_who_cannot_see_the_node_cannot_draft_from_it(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/api/outreach/draft", json={"node_id": PERSON}, headers=CONTRACTOR
        )
        assert response.status_code == 404
        # 404 rather than 403: a 403 would confirm the node exists to someone
        # who may not be entitled to know that (§6.3).
        assert "forbidden" not in response.text.lower()

    def test_the_ceo_can_draft_from_the_same_node(self, client: TestClient) -> None:
        """The counterweight. Without it the refusal above proves nothing."""
        response = client.post("/api/outreach/draft", json={"node_id": PERSON}, headers=CEO)
        assert response.status_code == 200
        assert response.json()["state"] == "pending"

    def test_restricted_content_is_refused_even_from_a_holder(
        self, client: TestClient, store: Path
    ) -> None:
        """The CEO holds every grant in this corpus and is still refused.

        This is the one check that fires against an authorised principal, and
        it is the whole reason the endpoint is not just an ACL projection.
        """
        node_id = a_restricted_node(store)
        response = client.post("/api/outreach/draft", json={"node_id": node_id}, headers=CEO)
        assert response.status_code == 403
        assert "restricted" in response.json()["detail"]

    def test_a_refused_draft_is_audited(self, client: TestClient, store: Path) -> None:
        node_id = a_restricted_node(store)
        client.post("/api/outreach/draft", json={"node_id": node_id}, headers=CEO)

        app = build_app(store)
        trail = app.audit(Surface.API).read(limit=50, action=Action.OUTREACH_REFUSED)
        assert trail, "a refused draft left no audit record"
        assert trail[0].outcome is Outcome.REFUSED
        assert node_id in trail[0].node_ids

    def test_outreach_needs_a_person(self, client: TestClient) -> None:
        documents = client.get("/api/nodes?type=Document", headers=CEO).json()
        response = client.post(
            "/api/outreach/draft", json={"node_id": documents[0]["id"]}, headers=CEO
        )
        assert response.status_code == 400

    def test_the_draft_never_carries_a_fact_its_author_cannot_read(
        self, client: TestClient
    ) -> None:
        """Facts come from edges, and edges are filtered by the same access
        filter the retrieval path uses. The comp canary is the probe."""
        draft = client.post("/api/outreach/draft", json={"node_id": PERSON}, headers=CEO).json()
        body = draft["body"] + " ".join(draft["facts"])
        assert "leadership-comp" not in body


class TestSendRequiresApproval:
    def test_a_pending_draft_cannot_be_sent(self, client: TestClient) -> None:
        draft = client.post("/api/outreach/draft", json={"node_id": PERSON}, headers=CEO).json()
        response = client.post(
            "/api/outreach/send", json={"draft_id": draft["draft_id"]}, headers=CEO
        )
        assert response.status_code == 409
        assert "approved" in response.json()["detail"]

    def test_an_unknown_draft_id_is_not_found(self, client: TestClient) -> None:
        response = client.post(
            "/api/outreach/send", json={"draft_id": "outreach-nobody-0000"}, headers=CEO
        )
        assert response.status_code == 404

    def test_approved_then_sent_once(self, client: TestClient, store: Path) -> None:
        draft = client.post("/api/outreach/draft", json={"node_id": PERSON}, headers=CEO).json()
        key = draft["draft_id"]

        client.post(
            "/api/review/decide",
            headers=CEO,
            json={"items": [{"key": key, "kind": "outreach"}], "decision": "accepted"},
        )
        first = client.post("/api/outreach/send", json={"draft_id": key}, headers=CEO)
        assert first.status_code == 200
        assert first.json()["state"] == "sent"
        assert first.json()["sent_by"] == "ceo"

        # Terminal. A replayed request must not send twice — the guard that
        # matters most the moment a real transport is attached.
        replay = client.post("/api/outreach/send", json={"draft_id": key}, headers=CEO)
        assert replay.status_code == 409

        app = build_app(store)
        sent = app.audit(Surface.API).read(limit=50, action=Action.OUTREACH_SEND)
        assert sent, "a send left no audit record"
        assert sent[0].actor == "ceo"
        assert sent[0].proposal_id == key
        assert PERSON in sent[0].node_ids

    def test_a_rejected_draft_cannot_be_sent(self, client: TestClient) -> None:
        draft = client.post("/api/outreach/draft", json={"node_id": PERSON}, headers=CEO).json()
        key = draft["draft_id"]
        client.post(
            "/api/review/decide",
            headers=CEO,
            json={"items": [{"key": key, "kind": "outreach"}], "decision": "rejected"},
        )
        assert (
            client.post("/api/outreach/send", json={"draft_id": key}, headers=CEO).status_code
            == 409
        )

    def test_a_sender_who_lost_access_cannot_dispatch(
        self, client: TestClient, store: Path
    ) -> None:
        """Grants are mirrored and eventually consistent, so access can be lost
        between drafting and sending — and the send is the irreversible half."""
        draft = client.post("/api/outreach/draft", json={"node_id": PERSON}, headers=CEO).json()
        client.post(
            "/api/review/decide",
            headers=CEO,
            json={
                "items": [{"key": draft["draft_id"], "kind": "outreach"}],
                "decision": "accepted",
            },
        )
        # The contractor cannot see the subject; approval by someone else does
        # not let them dispatch it.
        response = client.post(
            "/api/outreach/send",
            json={"draft_id": draft["draft_id"]},
            headers=CONTRACTOR,
        )
        assert response.status_code == 404


class TestQueueIntegration:
    def test_outreach_appears_in_the_review_queue(self, client: TestClient) -> None:
        draft = client.post("/api/outreach/draft", json={"node_id": PERSON}, headers=CEO).json()
        queue = client.get("/api/review", headers=CEO).json()
        item = next(i for i in queue if i["key"] == draft["draft_id"])
        assert item["kind"] == "outreach"
        # The reviewer needs the message itself, not a summary of it, in the
        # same request — one round trip per item is the 18-second budget.
        assert item["outreach"]["body"] == draft["body"]

    def test_the_listing_is_acl_projected(self, client: TestClient) -> None:
        """A draft quotes the graph, so listing one to a principal who cannot
        open its subject would route around that node's ACL."""
        client.post("/api/outreach/draft", json={"node_id": PERSON}, headers=CEO)
        assert client.get("/api/outreach", headers=CONTRACTOR).json() == []
        assert client.get("/api/outreach", headers=CEO).json()

    def test_stats_count_outreach_separately(self, client: TestClient) -> None:
        client.post("/api/outreach/draft", json={"node_id": PERSON}, headers=CEO)
        stats = client.get("/api/review/stats", headers=CEO).json()
        assert stats["pending_outreach"] >= 1
        assert stats["pending"] >= stats["pending_outreach"]


class TestStoreStateMachine:
    """The store's own guarantees, without the HTTP layer in the way."""

    def _draft(self, **overrides: object) -> OutreachDraft:
        from datetime import UTC, datetime

        base = {
            "draft_id": "outreach-ceo-test",
            "node_id": PERSON,
            "node_title": "Ana Brito",
            "sensitivity": Sensitivity.INTERNAL,
            "drafted_by": "ceo",
            "created_at": datetime(2024, 1, 1, tzinfo=UTC),
            "subject": "hello",
            "body": "hi",
            "facts": (),
            "lead": None,
            "lead_source": "offline",
        }
        return OutreachDraft(**{**base, **overrides})  # type: ignore[arg-type]

    def test_a_sent_draft_cannot_be_reopened(self, store: Path) -> None:
        """The one irreversible state. Offering an undo would be a lie."""
        app = build_app(store)
        drafts = OutreachStore(app.repo)
        drafts.put(self._draft(draft_id="outreach-ceo-reopen"))
        drafts.decide("outreach-ceo-reopen", OutreachState.APPROVED, reviewer="ceo")
        drafts.dispatch("outreach-ceo-reopen", sender="ceo")

        with pytest.raises(OutreachError, match="cannot be undone"):
            drafts.reopen("outreach-ceo-reopen", reviewer="ceo")

    def test_a_decided_draft_cannot_be_redrafted_into_pending(self, store: Path) -> None:
        """Re-drafting is idempotent by content address, so a rejected draft
        would otherwise be resurrected by simply asking again."""
        app = build_app(store)
        drafts = OutreachStore(app.repo)
        drafts.put(self._draft(draft_id="outreach-ceo-redraft"))
        drafts.decide("outreach-ceo-redraft", OutreachState.REJECTED, reviewer="ceo")

        with pytest.raises(OutreachError, match="cannot be re-drafted"):
            drafts.put(self._draft(draft_id="outreach-ceo-redraft"))

    def test_the_id_is_content_addressed(self) -> None:
        first = draft_id(PERSON, "ceo", "same body")
        assert first == draft_id(PERSON, "ceo", "same body")
        # Two people deciding to contact someone is corroboration, not a
        # collision — the author is part of the address.
        assert first != draft_id(PERSON, "eng-ic", "same body")

    def test_drafts_never_reach_the_node_tree(self, store: Path) -> None:
        """Invariant 1's neighbour: an outreach draft is not a graph claim, so
        approving one must not produce a node or an edge."""
        app = build_app(store)
        before = sorted(app.repo.walk_ids())
        drafts = OutreachStore(app.repo)
        drafts.put(self._draft(draft_id="outreach-ceo-notree"))
        drafts.decide("outreach-ceo-notree", OutreachState.APPROVED, reviewer="ceo")
        drafts.dispatch("outreach-ceo-notree", sender="ceo")
        assert sorted(app.repo.walk_ids()) == before


class TestLeadSource:
    def test_offline_returns_a_name_and_never_an_address(self) -> None:
        """A fabricated address is the one input that makes the reviewer's
        decision wrong while looking right."""
        lead = OfflineLeadSource().find("Ana Brito", organization="Finance")
        assert lead is not None
        assert lead.name == "Ana Brito"
        assert lead.email is None
        assert lead.source == "offline"
        assert not lead.contactable

    def test_offline_is_chosen_without_a_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("APOLLO_API_KEY", raising=False)
        monkeypatch.delenv("COMPANY_BRAIN_OFFLINE", raising=False)
        provider = choose_lead_source()
        assert not provider.live
        assert "APOLLO_API_KEY" in provider.reason

    def test_forced_offline_beats_a_present_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The switch that keeps CI free has to work here too, or a populated
        .env silently starts billing an outreach test."""
        monkeypatch.setenv("APOLLO_API_KEY", "secret")
        monkeypatch.setenv("COMPANY_BRAIN_OFFLINE", "1")
        provider = choose_lead_source()
        assert not provider.live
        assert provider.source.name == "offline"

    def test_a_miss_is_not_an_error(self) -> None:
        """Most people in an internal graph are not in Apollo's database, so a
        404 has to be the common case rather than a failed request."""
        import httpx

        transport = httpx.MockTransport(lambda _: httpx.Response(404))
        client = ApolloClient("k", client=httpx.Client(transport=transport))
        assert client.find("Nobody Here") is None

    def test_a_rate_limit_is_an_error(self) -> None:
        import httpx

        transport = httpx.MockTransport(lambda _: httpx.Response(429))
        client = ApolloClient("k", client=httpx.Client(transport=transport))
        with pytest.raises(ApolloError, match="rate limit"):
            client.find("Ana Brito")

    def test_a_match_is_parsed_and_never_asks_for_personal_email(self) -> None:
        import httpx

        seen: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            import json

            seen.update(json.loads(request.content))
            return httpx.Response(
                200,
                json={
                    "person": {
                        "name": "Ana Brito",
                        "email": "ana@example.com",
                        "title": "Finance Lead",
                        "organization": {"name": "Acme"},
                        "linkedin_url": "https://example.com/in/ana",
                    }
                },
            )

        client = ApolloClient("k", client=httpx.Client(transport=httpx.MockTransport(handler)))
        lead = client.find("Ana Brito", organization="Acme")

        assert lead == Lead(
            name="Ana Brito",
            email="ana@example.com",
            title="Finance Lead",
            organization="Acme",
            linkedin_url="https://example.com/in/ana",
            source="apollo",
        )
        # It bills per call and returns addresses people did not offer.
        assert "reveal_personal_emails" not in seen


class TestCompose:
    def test_the_body_says_only_what_it_was_given(self) -> None:
        """Templated rather than model-written: a synthesized outreach message
        would need the citation validator in front of it, and prose addressed
        to a person has no honest version of that check yet."""
        subject, body = compose(
            node_title="Ana Brito",
            node_type="Person",
            facts=["authored Quarterly close runbook"],
            lead=None,
            sender_display="Chief Executive",
        )
        assert "Quarterly close runbook" in subject
        assert "authored Quarterly close runbook" in body
        assert body.endswith("Chief Executive")

    def test_a_draft_with_no_facts_says_so(self) -> None:
        """Padding an empty draft would hide from the reviewer that there is
        nothing behind it."""
        _, body = compose(
            node_title="Ana Brito",
            node_type="Person",
            facts=[],
            lead=None,
            sender_display="Chief Executive",
        )
        assert "nothing more specific" in body
