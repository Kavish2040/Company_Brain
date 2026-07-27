"""A simulated Slack workspace.

Not a mock — a working connector over mutable in-memory state. Messages can be
posted, edited and deleted; people can join and leave channels. That makes the
M2 problems testable without credentials: an edit really does change a content
hash, a deletion really does disappear from enumeration, and a departure really
does remove a grant.

The real Slack connector replaces `fetch`/`enumerate_ids`/`grants` with API
calls and keeps everything else. What it will *not* be able to keep is the
convenience of `enumerate_ids()` being cheap — see the note there.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from company_brain.connectors.base import Connector, Grant, Page, SourceRecord
from company_brain.schemas.acl import AclRef, Sensitivity

EPOCH = datetime(2024, 5, 1, 9, 0, tzinfo=UTC)


@dataclass
class Message:
    ts: str
    user: str
    text: str
    edited_at: str | None = None

    def to_json(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "type": "message",
            "user": self.user,
            "text": self.text,
            "ts": self.ts,
        }
        if self.edited_at:
            payload["edited"] = {"ts": self.edited_at}
        return payload


@dataclass
class Channel:
    id: str
    name: str
    sensitivity: Sensitivity
    members: set[str] = field(default_factory=set)
    messages: dict[str, Message] = field(default_factory=dict)
    # Monotonic per-channel revision, standing in for Slack's cursor.
    revision: int = 0


class SimulatedSlack:
    """A Slack workspace you can mutate, for exercising the sync engine."""

    name = "slack"

    def __init__(self) -> None:
        self.channels: dict[str, Channel] = {}
        self._clock = EPOCH
        self._seq = 0

    # ---- workspace mutation (the test's lever) ---------------------------

    def add_channel(
        self, cid: str, name: str, sensitivity: Sensitivity, members: set[str]
    ) -> Channel:
        channel = Channel(id=cid, name=name, sensitivity=sensitivity, members=set(members))
        self.channels[cid] = channel
        return channel

    def post(self, cid: str, user: str, text: str) -> str:
        channel = self.channels[cid]
        self._seq += 1
        ts = f"{(self._clock + timedelta(minutes=self._seq)).timestamp():.6f}"
        channel.messages[ts] = Message(ts=ts, user=user, text=text)
        channel.revision += 1
        return ts

    def edit(self, cid: str, ts: str, text: str) -> None:
        channel = self.channels[cid]
        message = channel.messages[ts]
        message.text = text
        self._seq += 1
        message.edited_at = f"{(self._clock + timedelta(minutes=self._seq)).timestamp():.6f}"
        channel.revision += 1

    def delete(self, cid: str, ts: str) -> None:
        channel = self.channels[cid]
        del channel.messages[ts]
        channel.revision += 1

    def join(self, cid: str, principal: str) -> None:
        self.channels[cid].members.add(principal)

    def leave(self, cid: str, principal: str) -> None:
        self.channels[cid].members.discard(principal)

    # ---- Connector -------------------------------------------------------

    def _external_id(self, cid: str) -> str:
        return f"{cid}/day"

    def _record(self, channel: Channel) -> SourceRecord:
        """One record per channel — the day's transcript, as an export file."""
        payload = [m.to_json() for m in sorted(channel.messages.values(), key=lambda m: m.ts)]
        raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
        stamps = sorted(float(m.ts) for m in channel.messages.values())
        return SourceRecord(
            external_id=self._external_id(channel.id),
            # The version is what makes change detection cheap: an unchanged
            # channel is skipped before we ever hash its content.
            external_version=f"rev-{channel.revision}",
            uri=f"slack://workspace/{channel.id}",
            suffix=".json",
            raw=raw,
            acl=AclRef(ref=f"slack:channel:{channel.id}", sensitivity=channel.sensitivity),
            created=datetime.fromtimestamp(stamps[0], tz=UTC) if stamps else None,
            modified=datetime.fromtimestamp(stamps[-1], tz=UTC) if stamps else None,
        )

    def fetch(self, cursor: str | None) -> Page:
        """Everything changed since the cursor.

        The cursor is a per-channel revision map. Real Slack gives a
        `conversations.history` cursor plus `oldest`; the shape is the same —
        resume from a token, get only what moved.
        """
        seen: dict[str, int] = json.loads(cursor) if cursor else {}
        records = [
            self._record(channel)
            for cid, channel in sorted(self.channels.items())
            if channel.messages and channel.revision > seen.get(cid, -1)
        ]
        now = {cid: c.revision for cid, c in self.channels.items()}
        return Page(records=tuple(records), cursor=json.dumps(now, sort_keys=True))

    def enumerate_ids(self) -> set[str]:
        """Full enumeration, for delete detection.

        Cheap here. Against real Slack it is a `conversations.list` plus a
        `conversations.history` per channel — which is why deletion freshness is
        an SLA ("reflected within 24h"), not an immediate guarantee (§9.3).
        """
        return {
            self._external_id(cid) for cid, channel in self.channels.items() if channel.messages
        }

    def grants(self) -> Iterator[Grant]:
        for cid, channel in sorted(self.channels.items()):
            for principal in sorted(channel.members):
                yield Grant(
                    principal_id=principal,
                    acl_ref=f"slack:channel:{cid}",
                    sensitivity=channel.sensitivity,
                )


def seeded_workspace() -> SimulatedSlack:
    """A workspace matching the synthetic corpus, for the `cb sync` demo.

    Without this the CLI built an *empty* SimulatedSlack, and reconciliation
    correctly concluded that every slack:* grant should be revoked — the engine
    behaving properly against a source that says nothing exists. Right answer,
    catastrophic demo.
    """
    from company_brain.corpus.generate import CHANNELS, PEOPLE

    workspace = SimulatedSlack()
    for cid, name, tier in CHANNELS:
        sensitivity = Sensitivity(tier)
        if name == "leadership-comp":
            members = {"ceo"}
        elif name == "general":
            members = {"ceo", "support-lead", "eng-ic", "contractor"}
        elif name == "support":
            members = {"ceo", "support-lead"}
        elif name == "finance":
            members = {"ceo"}
        else:
            members = {"ceo", "support-lead", "eng-ic"}
        workspace.add_channel(cid, name, sensitivity, members)
        speaker = PEOPLE[hash(cid) % len(PEOPLE)]
        workspace.post(cid, speaker.slack_id, f"Opening message in #{name}.")
    return workspace


def _assert_protocol() -> None:
    _: Connector = SimulatedSlack()


_assert_protocol()
