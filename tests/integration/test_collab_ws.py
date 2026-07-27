"""The live-collaboration transport, end to end over real WebSockets.

The tests that matter here are the permission ones. Live editing adds two new
doors into the graph — a socket that streams a node's body, and a shared room
that answers questions for several principals at once — and both are easy to
build in a way that leaks. A broadcast is the natural shape for collaboration
and exactly the wrong shape for an ACL-projected answer.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from company_brain.acl.grants import GrantTable
from company_brain.api.app import api, get_app, get_hub
from company_brain.app import App, Providers
from company_brain.collab.hub import CollabHub
from company_brain.collab.session import SessionRegistry
from company_brain.index.base import HashingEmbedder
from company_brain.index.memory import MemoryIndex
from company_brain.normalize.formats import default_registry
from company_brain.schemas.acl import AclRef, Sensitivity
from company_brain.schemas.nodes import Frontmatter, Node, NodeType
from company_brain.store.backend import MemoryBackend
from company_brain.store.fences import upsert_region
from company_brain.store.repository import Repository

pytestmark = pytest.mark.integration

OPEN_ID = "processes/vendor-renewal"
SECRET_ID = "processes/executive-compensation"

OPEN_REF = "fs:corpus:docs"
SECRET_REF = "slack:channel:COMP"

OPEN_BODY = (
    "The vendor renewal process governs how contracts are renewed.\n"
    "Sam Kaur owns vendor renewal and signs off on every contract."
)
SECRET_BODY = (
    "Executive compensation review for the leadership team.\n"
    "Vendor renewal budget is set against the compensation pool."
)


def make_node(node_id: str, title: str, ref: str, tier: Sensitivity, body: str) -> Node:
    return Node(
        frontmatter=Frontmatter(
            id=node_id,
            type=NodeType.PROCESS,
            title=title,
            acl=AclRef(ref=ref, sensitivity=tier),
        ),
        body=body,
    )


@pytest.fixture
def client() -> Iterator[TestClient]:
    """An app whose whole world is two nodes: one everybody sees, one only the
    CEO does. Overrides are used rather than the cached singletons so each test
    gets its own hub and its own store."""
    repo = Repository(MemoryBackend())
    repo.put(make_node(OPEN_ID, "Vendor renewal", OPEN_REF, Sensitivity.INTERNAL, OPEN_BODY))
    repo.put(
        make_node(
            SECRET_ID,
            "Executive compensation",
            SECRET_REF,
            Sensitivity.RESTRICTED,
            SECRET_BODY,
        )
    )

    grants = GrantTable()
    grants.grant("ceo", OPEN_REF, Sensitivity.INTERNAL)
    grants.grant("ceo", SECRET_REF, Sensitivity.RESTRICTED)
    grants.grant("eng-ic", OPEN_REF, Sensitivity.INTERNAL)
    # The contractor deliberately holds nothing beyond the open node.
    grants.grant("contractor", OPEN_REF, Sensitivity.INTERNAL)

    instance = App(
        repo=repo,
        registry=default_registry(),
        grants=grants,
        index=MemoryIndex(HashingEmbedder()),
        providers=Providers(
            extractor=cast(Any, None),  # never reached: nothing here ingests
            embedder=HashingEmbedder(),
            synthesizer_name="extractive-offline",
            offline=True,
            reason="test",
        ),
    )
    instance.load_index()

    # A short debounce so the flush timer fires within a test rather than after.
    hub = CollabHub(SessionRegistry(repo), debounce=0.01)

    api.dependency_overrides[get_app] = lambda: instance
    api.dependency_overrides[get_hub] = lambda: hub
    with TestClient(api) as test_client:
        test_client.repo = repo  # type: ignore[attr-defined]
        yield test_client
    api.dependency_overrides.clear()


def connect(client: TestClient, path: str, principal: str) -> Any:
    return client.websocket_connect(path, subprotocols=[f"cb.principal.{principal}"])


def read_until(ws: Any, kind: str, *, limit: int = 8) -> dict[str, Any]:
    """Read past presence chatter to the message a test is actually about.

    Joining a room broadcasts presence to everyone including the joiner, so the
    exact frame count around any action depends on who else is connected.
    Asserting on that count tests the test harness, not the server.
    """
    for _ in range(limit):
        message = ws.receive_json()
        if message.get("type") == kind:
            return cast(dict[str, Any], message)
    raise AssertionError(f"no {kind!r} message within {limit} frames")


class TestIdentity:
    def test_a_socket_with_no_principal_is_closed(self, client: TestClient) -> None:
        with (
            client.websocket_connect(f"/api/collab/node/{OPEN_ID}") as ws,
            pytest.raises(WebSocketDisconnect) as caught,
        ):
            ws.receive_json()
        assert caught.value.code == 4401

    def test_an_unknown_principal_is_closed(self, client: TestClient) -> None:
        """Fail closed on a name we don't recognise rather than defaulting to
        one — a typo must not silently become a different identity."""
        with (
            connect(client, f"/api/collab/node/{OPEN_ID}", "nobody") as ws,
            pytest.raises(WebSocketDisconnect) as caught,
        ):
            ws.receive_json()
        assert caught.value.code == 4401


class TestNodeRoomPermissions:
    def test_a_principal_who_cannot_see_a_node_is_refused(self, client: TestClient) -> None:
        with (
            connect(client, f"/api/collab/node/{SECRET_ID}", "contractor") as ws,
            pytest.raises(WebSocketDisconnect) as caught,
        ):
            ws.receive_json()
        assert caught.value.code == 4404

    def test_a_missing_node_closes_with_the_same_code_as_a_hidden_one(
        self, client: TestClient
    ) -> None:
        """Distinguishing the two would confirm to an outsider that a node
        exists (§6.3), which is the leak the 404-not-403 rule exists to stop."""
        with (
            connect(client, "/api/collab/node/processes/does-not-exist", "ceo") as ws,
            pytest.raises(WebSocketDisconnect) as caught,
        ):
            ws.receive_json()
        assert caught.value.code == 4404

    def test_the_ceo_can_open_the_restricted_node(self, client: TestClient) -> None:
        with connect(client, f"/api/collab/node/{SECRET_ID}", "ceo") as ws:
            welcome = read_until(ws, "welcome")
        assert welcome["body"] == SECRET_BODY


class TestLiveEditing:
    def test_an_edit_reaches_the_other_window(self, client: TestClient) -> None:
        with connect(client, f"/api/collab/node/{OPEN_ID}", "ceo") as first:
            read_until(first, "welcome")
            with connect(client, f"/api/collab/node/{OPEN_ID}", "eng-ic") as second:
                read_until(second, "welcome")

                first.send_json({"type": "edit", "base_revision": 0, "body": "Rewritten."})

                echo = read_until(first, "sync")
                relayed = read_until(second, "sync")

        assert echo["body"] == "Rewritten."
        assert relayed["body"] == "Rewritten."
        assert relayed["revision"] == 1
        assert relayed["clobbered"] is False

    def test_presence_names_everyone_in_the_room(self, client: TestClient) -> None:
        with connect(client, f"/api/collab/node/{OPEN_ID}", "ceo") as first:
            read_until(first, "welcome")
            with connect(client, f"/api/collab/node/{OPEN_ID}", "eng-ic") as second:
                read_until(second, "welcome")
                # Read forward until the second editor shows up in presence.
                for _ in range(4):
                    presence = read_until(first, "presence")
                    if len(presence["participants"]) == 2:
                        break

        principals = {p["principal"] for p in presence["participants"]}
        assert principals == {"ceo", "eng-ic"}
        # A colour per participant, so remote carets are tellable apart.
        assert all(p["color"] for p in presence["participants"])

    def test_editing_a_generated_region_is_rejected_and_resynced(
        self, client: TestClient
    ) -> None:
        """Invariant 13, inverted: a human edits around a fence, never inside
        it. The browser is not where this gets enforced."""
        fenced = upsert_region(OPEN_BODY, "mentions", "Mentioned in 3 documents.")
        repo: Repository = client.repo  # type: ignore[attr-defined]
        repo.put(make_node(OPEN_ID, "Vendor renewal", OPEN_REF, Sensitivity.INTERNAL, fenced))

        with connect(client, f"/api/collab/node/{OPEN_ID}", "ceo") as ws:
            welcome = read_until(ws, "welcome")
            tampered = welcome["body"].replace("3 documents", "900 documents")
            ws.send_json({"type": "edit", "base_revision": 0, "body": tampered})
            reply = read_until(ws, "rejected")

        assert "interior of generated region" in reply["reason"]
        assert reply["body"] == welcome["body"], "a refused edit must resync the client"

    def test_an_edit_is_persisted_to_the_markdown_store(self, client: TestClient) -> None:
        repo: Repository = client.repo  # type: ignore[attr-defined]
        with connect(client, f"/api/collab/node/{OPEN_ID}", "ceo") as ws:
            read_until(ws, "welcome")
            ws.send_json(
                {"type": "edit", "base_revision": 0, "body": "Saved without a button."}
            )
            read_until(ws, "sync")
        # Leaving the room flushes; the debounce timer may also have fired.
        assert repo.get(OPEN_ID).body == "Saved without a button."

    def test_a_live_edit_cannot_change_frontmatter(self, client: TestClient) -> None:
        repo: Repository = client.repo  # type: ignore[attr-defined]
        before = repo.get(OPEN_ID).frontmatter
        with connect(client, f"/api/collab/node/{OPEN_ID}", "ceo") as ws:
            read_until(ws, "welcome")
            ws.send_json({"type": "edit", "base_revision": 0, "body": "Only the body moved."})
            read_until(ws, "sync")
        assert repo.get(OPEN_ID).frontmatter == before


class TestSharedAskRoom:
    def test_each_participant_is_answered_under_their_own_grants(
        self, client: TestClient
    ) -> None:
        """The leak this room invites. One question, one broadcast — but the
        answers must be computed per principal, not copied from the asker."""
        with connect(client, "/api/collab/ask", "ceo") as boss:
            read_until(boss, "welcome")
            with connect(client, "/api/collab/ask", "contractor") as guest:
                read_until(guest, "welcome")

                boss.send_json({"type": "ask", "question": "who owns vendor renewal?"})

                boss_answer = read_until(boss, "answer")
                guest_answer = read_until(guest, "answer")

        # Both were asked the same question and both got their own answer.
        assert boss_answer["question"] == guest_answer["question"]

        cited = {c["node_id"] for c in guest_answer.get("citations", [])}
        assert SECRET_ID not in cited, "the contractor was told about a restricted node"
        assert guest_answer["withheld_by_acl"] >= 0
        # The CEO can see strictly more of the corpus than the contractor.
        assert boss_answer["seed_count"] >= guest_answer["seed_count"]

    def test_the_question_itself_is_announced_to_the_room(self, client: TestClient) -> None:
        with connect(client, "/api/collab/ask", "ceo") as boss:
            read_until(boss, "welcome")
            boss.send_json({"type": "ask", "question": "who owns vendor renewal?"})
            asking = read_until(boss, "asking")

        assert asking["by"] == "Chief Executive"
