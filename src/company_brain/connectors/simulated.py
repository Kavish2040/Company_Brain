"""A simulated Slack workspace, with state that survives the process.

Not a mock — a working connector over mutable state persisted to
``store/_sim/slack.json``. Messages can be edited, days can disappear, people
join and leave. That makes the M2 problems demonstrable from a terminal, not
only from inside pytest.

Three things this gets right that the earlier in-memory version did not:

**It serves the corpus's own channel-days.** The earlier version fabricated a
one-line message per channel at a made-up date, so every sync *added* nodes
alongside the corpus's rather than updating them — and `cb ask` could then cite
the junk. Records now carry the corpus's exact URI
(``file://corpus/slack/<channel>/<date>.json``) and path, so they resolve to
the node ids the initial ingest already created, and a sync over an unchanged
workspace is a genuine no-op.

**It is deterministic.** The old version chose a speaker with ``hash(cid)``.
Python randomises string hashing per process, so that byte landed in the record
JSON, moved ``content_sha256`` on every run, and produced phantom updates that
busted the extraction cache — real spend against a live model.

**Membership has one source.** ``CHANNEL_MEMBERS`` in corpus/generate.py,
shared with ``build_grants()``. The two used to be written out separately and
agreed only by luck; grant reconciliation is correct only while they match.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from company_brain.connectors.base import (
    Connector,
    Disappearance,
    Grant,
    Page,
    SourceRecord,
)
from company_brain.schemas.acl import AclRef, Sensitivity
from company_brain.store.backend import StoreBackend

STATE_PATH = "_sim/slack.json"
# Only used by hand-built workspaces; corpus-seeded days carry their own dates.
DEFAULT_DATE = "2024-05-01"
EPOCH = datetime(2024, 5, 1, 9, 0, tzinfo=UTC)
CORPUS_SLACK = Path("corpus/synthetic/slack")


@dataclass
class Day:
    """One channel-day — the unit the corpus stores and the graph nodes."""

    date: str
    messages: list[dict[str, object]] = field(default_factory=list)
    revision: int = 0
    # Why this day is no longer visible, if it isn't. Carried explicitly so the
    # three signals an enumeration diff collapses into one stay separable.
    gone: str | None = None  # None | "deleted" | "trashed" | "unshared"


@dataclass
class Channel:
    id: str
    name: str
    sensitivity: Sensitivity
    members: set[str] = field(default_factory=set)
    days: dict[str, Day] = field(default_factory=dict)

    @property
    def messages(self) -> dict[str, dict[str, object]]:
        """Every message across every day, keyed by ts.

        A read-only flattening. Days are the storage unit because that is what
        the corpus stores and what a node maps to, but "the messages in this
        channel" is the question callers usually have.
        """
        return {
            str(m["ts"]): m
            for day in sorted(self.days.values(), key=lambda d: d.date)
            for m in day.messages
            if m.get("ts")
        }


class SimulatedSlack:
    """A Slack workspace with persistent, mutable state."""

    name = "slack"

    def __init__(self, channels: dict[str, Channel] | None = None) -> None:
        self.channels: dict[str, Channel] = channels if channels is not None else {}
        self._seq = 0

    # ---- persistence -----------------------------------------------------

    @classmethod
    def load(cls, backend: StoreBackend) -> SimulatedSlack | None:
        raw = backend.read_text(STATE_PATH)
        if raw is None:
            return None
        data = json.loads(raw)
        return cls(
            {
                cid: Channel(
                    id=cid,
                    name=c["name"],
                    sensitivity=Sensitivity(c["sensitivity"]),
                    members=set(c["members"]),
                    days={
                        d["date"]: Day(
                            date=d["date"],
                            messages=d["messages"],
                            revision=d["revision"],
                            gone=d.get("gone"),
                        )
                        for d in c["days"]
                    },
                )
                for cid, c in data["channels"].items()
            }
        )

    def save(self, backend: StoreBackend) -> None:
        payload = {
            "channels": {
                cid: {
                    "name": c.name,
                    "sensitivity": str(c.sensitivity),
                    "members": sorted(c.members),
                    "days": [
                        {
                            "date": d.date,
                            "messages": d.messages,
                            "revision": d.revision,
                            "gone": d.gone,
                        }
                        for d in sorted(c.days.values(), key=lambda day: day.date)
                    ],
                }
                for cid, c in sorted(self.channels.items())
            }
        }
        backend.write_text(STATE_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n")

    # ---- construction (hand-built workspaces, mostly for tests) ----------

    def add_channel(
        self, cid: str, name: str, sensitivity: Sensitivity, members: set[str]
    ) -> Channel:
        channel = Channel(id=cid, name=name, sensitivity=sensitivity, members=set(members))
        self.channels[cid] = channel
        return channel

    def post(self, key: str, user: str, text: str, date: str = DEFAULT_DATE) -> str:
        """Append a message. Returns its ts, which is also its handle."""
        channel = self.channel(key)
        day = channel.days.setdefault(date, Day(date=date))
        self._seq += 1
        ts = f"{(EPOCH + timedelta(minutes=self._seq)).timestamp():.6f}"
        day.messages.append({"type": "message", "user": user, "text": text, "ts": ts})
        day.revision += 1
        return ts

    def edit(self, key: str, ts: str, text: str) -> None:
        for day in self.channel(key).days.values():
            for message in day.messages:
                if message.get("ts") == ts:
                    message["text"] = text
                    message["edited"] = {"ts": ts}
                    day.revision += 1
                    return
        raise KeyError(f"no message {ts!r} in {key!r}")

    def delete(self, key: str, ts: str) -> None:
        for day in self.channel(key).days.values():
            before = len(day.messages)
            day.messages = [m for m in day.messages if m.get("ts") != ts]
            if len(day.messages) != before:
                day.revision += 1
                if not day.messages:
                    day.gone = "deleted"
                return
        raise KeyError(f"no message {ts!r} in {key!r}")

    # ---- scenario levers -------------------------------------------------

    def channel(self, key: str) -> Channel:
        """Look up by channel id or by name — callers reasonably use both."""
        if key in self.channels:
            return self.channels[key]
        for channel in self.channels.values():
            if channel.name == key:
                return channel
        known = ", ".join(sorted(c.name for c in self.channels.values()))
        raise KeyError(f"no channel {key!r}; have: {known}")

    def channel_by_name(self, name: str) -> Channel:
        return self.channel(name)

    def latest_day(self, name: str) -> Day:
        channel = self.channel(name)
        live = [d for d in channel.days.values() if d.gone is None and d.messages]
        if not live:
            raise KeyError(f"#{name} has no visible days left")
        return max(live, key=lambda d: d.date)

    def edit_latest(self, name: str, text: str) -> str:
        """Rewrite the newest message of a channel's latest day."""
        day = self.latest_day(name)
        newest = max(day.messages, key=lambda m: str(m.get("ts", "")))
        newest["text"] = text
        newest["edited"] = {"ts": newest["ts"]}
        day.revision += 1
        return day.date

    def mark_gone(self, name: str, how: str) -> str:
        """Make the latest day disappear, recording *why* it did."""
        day = self.latest_day(name)
        day.gone = how
        return day.date

    def restore(self, name: str) -> None:
        for day in self.channel(name).days.values():
            day.gone = None

    def join(self, key: str, principal: str) -> None:
        self.channel(key).members.add(principal)

    def leave(self, key: str, principal: str) -> None:
        self.channel(key).members.discard(principal)

    # ---- Connector -------------------------------------------------------

    def _external_id(self, channel: Channel, day: Day) -> str:
        return f"{channel.name}/{day.date}"

    def _record(self, channel: Channel, day: Day) -> SourceRecord:
        """Byte-identical to the corpus file, so content hashes agree."""
        raw = (json.dumps(day.messages, indent=2, sort_keys=True) + "\n").encode()
        stamps = sorted(float(str(m["ts"])) for m in day.messages if m.get("ts"))
        return SourceRecord(
            external_id=self._external_id(channel, day),
            external_version=f"rev-{day.revision}",
            # The corpus's own URI and path. Identical inputs to document_slug
            # mean an identical node id, so this connector *updates* the
            # corpus's nodes instead of shadowing them with a second copy.
            uri=f"file://corpus/slack/{channel.name}/{day.date}.json",
            path=f"slack/{channel.name}",
            suffix=".json",
            raw=raw,
            acl=AclRef(ref=f"slack:channel:{channel.id}", sensitivity=channel.sensitivity),
            created=datetime.fromtimestamp(stamps[0], tz=UTC) if stamps else None,
            modified=datetime.fromtimestamp(stamps[-1], tz=UTC) if stamps else None,
        )

    def fetch(self, cursor: str | None) -> Page:
        seen: dict[str, int] = json.loads(cursor) if cursor else {}
        records: list[SourceRecord] = []
        now: dict[str, int] = {}
        skipped = 0

        for channel in sorted(self.channels.values(), key=lambda c: c.id):
            for day in sorted(channel.days.values(), key=lambda d: d.date):
                key = self._external_id(channel, day)
                now[key] = day.revision
                if day.gone is not None or not day.messages:
                    continue
                if day.revision > seen.get(key, -1):
                    records.append(self._record(channel, day))
                else:
                    skipped += 1

        return Page(
            records=tuple(records),
            cursor=json.dumps(now, sort_keys=True),
            cursor_skipped=skipped,
        )

    def enumerate_ids(self) -> set[str]:
        return {
            self._external_id(c, d)
            for c in self.channels.values()
            for d in c.days.values()
            if d.gone is None and d.messages
        }

    def classify_departure(self, external_id: str) -> Disappearance:
        """Why this day stopped appearing.

        Real Slack cannot distinguish most of these — `conversations.history`
        on a channel you left and one that was archived return the same error.
        The simulation carries the reason explicitly so the *engine's* handling
        of each is demonstrable; a real connector returns UNKNOWN wherever it
        genuinely cannot tell, and the engine then leaves the document alone.
        """
        name, _, date = external_id.partition("/")
        try:
            day = self.channel(name).days.get(date)
        except KeyError:
            return Disappearance.UNKNOWN
        if day is None:
            return Disappearance.UNKNOWN
        return {
            "deleted": Disappearance.DELETED,
            "trashed": Disappearance.TRASHED,
            "unshared": Disappearance.ACCESS_LOST,
        }.get(day.gone or "", Disappearance.UNKNOWN)

    def grants(self) -> Iterator[Grant]:
        for channel in sorted(self.channels.values(), key=lambda c: c.id):
            for principal in sorted(channel.members):
                yield Grant(
                    principal_id=principal,
                    acl_ref=f"slack:channel:{channel.id}",
                    sensitivity=channel.sensitivity,
                )


def seed_from_corpus(corpus: Path = CORPUS_SLACK) -> SimulatedSlack:
    """Build a workspace from the committed corpus.

    The workspace *is* the source those files came from, so it serves them
    verbatim. A sync against a freshly seeded workspace therefore changes
    nothing — the only honest starting state for a demo.
    """
    from company_brain.corpus.generate import CHANNEL_MEMBERS, CHANNELS

    workspace = SimulatedSlack()
    for cid, name, tier in CHANNELS:
        channel = Channel(
            id=cid,
            name=name,
            sensitivity=Sensitivity(tier),
            members=set(CHANNEL_MEMBERS.get(name, frozenset())),
        )
        directory = corpus / name
        if directory.is_dir():
            for path in sorted(directory.glob("*.json")):
                channel.days[path.stem] = Day(
                    date=path.stem, messages=json.loads(path.read_text()), revision=0
                )
        workspace.channels[cid] = channel
    return workspace


def load_or_seed(backend: StoreBackend, corpus: Path = CORPUS_SLACK) -> SimulatedSlack:
    """The workspace in whatever state it was last left.

    Persistence is what makes the scenarios composable at all. With an
    in-memory workspace, every invocation rebuilt at revision 0 while the
    cursor persisted — so a second `cb sync` reported nothing whatsoever, and
    no mutation could survive long enough to be synced.
    """
    existing = SimulatedSlack.load(backend)
    if existing is not None:
        return existing
    workspace = seed_from_corpus(corpus)
    workspace.save(backend)
    return workspace


def _assert_protocol() -> None:
    _: Connector = SimulatedSlack()


_assert_protocol()
