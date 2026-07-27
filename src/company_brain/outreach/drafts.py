"""Outreach drafts: composed from the graph, decided by a human, then dispatched.

Three states and two decisions, kept apart on purpose:

    pending --accept--> approved --dispatch--> sent
       |
       +----reject----> rejected

Approval and dispatch are separate acts because they answer different
questions. Approving says "this message is correct and this person should get
it"; dispatching says "send it now". Collapsing them would mean a reviewer
clearing a queue could not distinguish reading from acting, which is the same
reason the review queue does not auto-apply.

**Nothing here writes to the canonical store.** Drafts live under
``store/_outreach/`` as JSON sidecars — workflow state in the same category as
``store/_sync/`` and ``store/_proposals/``'s queue rows, explicitly outside
invariant 2. That is also why they carry wall-clock timestamps, which invariant
4 keeps out of canonical files.

**A draft records the tier it was composed from.** The API refuses to draft
from restricted content at all, but the tier travels on the record anyway, so
the refusal is auditable after the fact rather than only enforceable before it.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from company_brain.outreach.apollo import Lead
from company_brain.schemas.acl import Sensitivity
from company_brain.store.repository import Repository

OUTREACH_PREFIX = "_outreach"

# Enough relations to ground a short message without turning it into a dossier.
# A draft that recites forty edges is one nobody reads before approving.
MAX_FACTS = 6


class OutreachError(RuntimeError):
    """A draft could not be stored, found, or moved to the requested state."""


class OutreachState(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class OutreachDraft:
    """One drafted message and everything a reviewer needs to judge it."""

    draft_id: str
    node_id: str
    node_title: str
    sensitivity: Sensitivity
    drafted_by: str
    created_at: datetime
    subject: str
    body: str
    # The graph statements the body was built from, verbatim, so the reviewer
    # checks the source rather than the prose. Same principle as edge evidence.
    facts: tuple[str, ...]
    lead: Lead | None
    lead_source: str
    state: OutreachState = OutreachState.PENDING
    decided_by: str | None = None
    decided_at: datetime | None = None
    sent_by: str | None = None
    sent_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "draft_id": self.draft_id,
            "node_id": self.node_id,
            "node_title": self.node_title,
            "sensitivity": str(self.sensitivity),
            "drafted_by": self.drafted_by,
            "created_at": _iso(self.created_at),
            "subject": self.subject,
            "body": self.body,
            "facts": list(self.facts),
            "lead": self.lead.to_dict() if self.lead else None,
            "lead_source": self.lead_source,
            "state": str(self.state),
            "decided_by": self.decided_by,
            "decided_at": _iso(self.decided_at) if self.decided_at else None,
            "sent_by": self.sent_by,
            "sent_at": _iso(self.sent_at) if self.sent_at else None,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> OutreachDraft:
        lead = raw.get("lead")
        decided, sent = raw.get("decided_at"), raw.get("sent_at")
        return cls(
            draft_id=str(raw["draft_id"]),
            node_id=str(raw["node_id"]),
            node_title=str(raw.get("node_title", "")),
            sensitivity=Sensitivity(raw["sensitivity"]),
            drafted_by=str(raw["drafted_by"]),
            created_at=_parse(str(raw["created_at"])),
            subject=str(raw.get("subject", "")),
            body=str(raw.get("body", "")),
            facts=tuple(raw.get("facts") or ()),
            lead=Lead.from_dict(lead) if isinstance(lead, dict) else None,
            lead_source=str(raw.get("lead_source", "offline")),
            state=OutreachState(raw.get("state", "pending")),
            decided_by=raw.get("decided_by"),
            decided_at=_parse(str(decided)) if decided else None,
            sent_by=raw.get("sent_by"),
            sent_at=_parse(str(sent)) if sent else None,
        )


def draft_id(node_id: str, drafted_by: str, body: str) -> str:
    """Content-addressed, like proposal ids.

    Drafting the same message for the same person twice is one queue entry, so
    a double-clicked button does not put two copies of the same outreach in
    front of a reviewer. The author is part of the address: two people
    independently deciding to contact someone is a fact worth keeping, not a
    collision to fold away.
    """
    digest = hashlib.blake2b(
        "\0".join((node_id, drafted_by, body)).encode("utf-8"), digest_size=8
    ).hexdigest()
    return f"outreach-{_slug(drafted_by)}-{digest}"


def compose(
    *,
    node_title: str,
    node_type: str,
    facts: Sequence[str],
    lead: Lead | None,
    sender_display: str,
) -> tuple[str, str]:
    """Build (subject, body) from graph statements alone.

    Deliberately templated rather than model-written. A synthesized outreach
    message would need the citation validator in front of it (invariant 11),
    and the honest version of that check for prose addressed to a person is not
    something this milestone has — so the body says only what the caller passed
    in as `facts`, each of which came from an edge a human can open.
    """
    who = (lead.name if lead else node_title).strip()
    first = who.split(" ")[0] if who else "there"
    topic = facts[0].split(" — ")[0] if facts else node_title

    subject = f"Quick question about {topic}"

    lines = [f"Hi {first},", ""]
    if facts:
        lines.append(f"We have {who} on record as a {node_type.lower()}:")
        lines.extend(f"  · {fact}" for fact in facts)
        lines.append("")
        lines.append(
            "I wanted to reach out about the above. If any of it is out of "
            "date, a correction would be genuinely useful."
        )
    else:
        # No edges to stand on. Say so rather than padding — a reviewer should
        # see that this draft has nothing behind it.
        lines.append(
            f"I wanted to reach out about your work. We have {who} on record "
            f"as a {node_type.lower()}, but nothing more specific."
        )
    lines.extend(["", "Thanks,", sender_display])
    return subject, "\n".join(lines)


class OutreachStore:
    """Read and write ``store/_outreach/``.

    Takes a :class:`Repository` for its backend only. It never calls ``put``,
    ``put_proposal``, or anything else that reaches the node tree — the type is
    here for the backend and the store root, not for graph access.
    """

    def __init__(self, repo: Repository, *, clock: Callable[[], datetime] = _now) -> None:
        self.repo = repo
        self._clock = clock

    # ---- write ---------------------------------------------------------

    def put(self, draft: OutreachDraft) -> OutreachDraft:
        """Store a draft, preserving the original `created_at` on a re-draft."""
        existing = self._read(draft.draft_id)
        if existing is not None:
            # Re-drafting something already decided must not quietly reset it
            # to pending and slip past the review it already failed.
            if existing.state is not OutreachState.PENDING:
                raise OutreachError(
                    f"{draft.draft_id} is already {existing.state}; "
                    f"it cannot be re-drafted into pending"
                )
            draft = replace(draft, created_at=existing.created_at)
        self._write(draft)
        return draft

    def decide(self, draft_id_: str, state: OutreachState, *, reviewer: str) -> OutreachDraft:
        """Approve or reject a pending draft. Retained either way."""
        if state not in (OutreachState.APPROVED, OutreachState.REJECTED):
            raise OutreachError(f"{state} is not a review decision")
        draft = self.get(draft_id_)
        if draft.state is not OutreachState.PENDING:
            raise OutreachError(f"{draft_id_} is already {draft.state}")
        decided = replace(
            draft,
            state=state,
            decided_by=reviewer,
            decided_at=self._clock().astimezone(UTC),
        )
        self._write(decided)
        return decided

    def reopen(self, draft_id_: str, *, reviewer: str) -> OutreachDraft:
        """Undo a decision — but never a dispatch.

        A rejection and an approval both only moved a row, so both are
        reversible. A send is not: whatever dispatch means, it has already
        happened, and offering an undo for it would be a lie in the one place
        this feature cannot afford one.
        """
        draft = self.get(draft_id_)
        if draft.state is OutreachState.SENT:
            raise OutreachError(f"{draft_id_} was already sent; a send cannot be undone")
        if draft.state is OutreachState.PENDING:
            raise OutreachError(f"{draft_id_} is already pending")
        reopened = replace(
            draft,
            state=OutreachState.PENDING,
            decided_by=reviewer,
            decided_at=self._clock().astimezone(UTC),
        )
        self._write(reopened)
        return reopened

    def dispatch(self, draft_id_: str, *, sender: str) -> OutreachDraft:
        """Mark an approved draft as sent.

        **No message leaves this system.** Apollo is wired for lead lookup only
        (see `apollo.py`), so this records that a human approved a dispatch and
        that it was actioned — it does not transmit anything. The state is
        real even though the transport is not yet: when a send channel does
        land, it plugs in here and every guard around it already exists.

        The guard that matters is the state check. `sent` is terminal, so a
        replayed request cannot double-send once a transport is attached.
        """
        draft = self.get(draft_id_)
        if draft.state is OutreachState.SENT:
            raise OutreachError(f"{draft_id_} was already sent")
        if draft.state is not OutreachState.APPROVED:
            raise OutreachError(
                f"{draft_id_} is {draft.state}; only an approved draft can be sent"
            )
        sent = replace(
            draft,
            state=OutreachState.SENT,
            sent_by=sender,
            sent_at=self._clock().astimezone(UTC),
        )
        self._write(sent)
        return sent

    # ---- read ----------------------------------------------------------

    def get(self, draft_id_: str) -> OutreachDraft:
        draft = self._read(draft_id_)
        if draft is None:
            raise OutreachError(f"no outreach draft {draft_id_!r}")
        return draft

    def records(self, *, state: OutreachState | None = None) -> list[OutreachDraft]:
        """Drafts, oldest first — the order a reviewer should work them in."""
        out = [d for d in self._scan() if state is None or d.state is state]
        out.sort(key=lambda d: (d.created_at, d.draft_id))
        return out

    def accept_rate(self) -> dict[str, tuple[int, int]]:
        """(approved, decided) for outreach, in the queue's calibration shape.

        Same question §11 asks of the extraction gates, asked of this path: if
        every draft is approved, the review step is a rubber stamp on messages
        going to real people.
        """
        approved = decided = 0
        for draft in self._scan():
            if draft.state is OutreachState.PENDING:
                continue
            decided += 1
            if draft.state is not OutreachState.REJECTED:
                approved += 1
        return {"outreach": (approved, decided)} if decided else {}

    # ---- internals -----------------------------------------------------

    def _path(self, draft_id_: str) -> str:
        return f"{OUTREACH_PREFIX}/{draft_id_}.json"

    def _read(self, draft_id_: str) -> OutreachDraft | None:
        text = self.repo.backend.read_text(self._path(draft_id_))
        if text is None:
            return None
        return OutreachDraft.from_dict(json.loads(text))

    def _write(self, draft: OutreachDraft) -> None:
        self.repo.backend.write_text(
            self._path(draft.draft_id),
            json.dumps(draft.to_dict(), indent=2, sort_keys=True) + "\n",
        )

    def _scan(self) -> Iterator[OutreachDraft]:
        for path in self.repo.backend.walk(OUTREACH_PREFIX):
            if not path.endswith(".json"):
                continue
            text = self.repo.backend.read_text(path)
            if text is None:
                continue
            try:
                yield OutreachDraft.from_dict(json.loads(text))
            except (ValueError, KeyError) as exc:
                raise OutreachError(f"corrupt outreach record at {path}: {exc}") from exc


def _slug(value: str) -> str:
    return "".join(c if c.isalnum() or c == "-" else "-" for c in value.lower())[:40]


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
