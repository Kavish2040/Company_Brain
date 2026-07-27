"""The connector contract, and what M2 actually has to get right.

A connector is not just "fetch documents". It owes three separate things, and
the second and third are where the difficulty lives:

1. **Content** — artifacts, incrementally, addressed by a cursor.
2. **Existence** — the full set of live external ids, so deletions can be
   detected. Most source systems do not push delete events reliably, so
   detection means periodic enumeration and diffing. That is a real cost at
   scale and needs a stated freshness SLA, not an implied one (§9.3).
3. **Permissions** — who can see each ACL ref, mirrored from the source. This
   is eventually consistent *by construction*: a membership change is visible
   only after the next sync. Every mirrored-permission system has that window.
   The honest posture is to bound it and measure it, which is what `synced_at`
   is for.

Sync state (cursors, the last-seen id set) is workflow state, not derived from
markdown, so it is not rebuildable by `index rebuild`. It lives under
`store/_sync/` today and moves to the Postgres `sources` table when the database
lands (ARCHITECTURE §5).
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable

from company_brain.schemas.acl import AclRef, Sensitivity
from company_brain.store.backend import StoreBackend

SYNC_PREFIX = "_sync"


@dataclass(frozen=True, slots=True)
class SourceRecord:
    """One artifact as the source system sees it."""

    external_id: str
    external_version: str
    uri: str
    suffix: str
    raw: bytes
    acl: AclRef
    # Only set when the source can tell us; never a local mtime, which changes
    # on checkout and would break byte-identical re-ingestion (invariant 4).
    created: datetime | None = None
    modified: datetime | None = None


@dataclass(frozen=True, slots=True)
class Grant:
    """One principal's access to one ACL ref, as the source reports it."""

    principal_id: str
    acl_ref: str
    sensitivity: Sensitivity


@dataclass(frozen=True, slots=True)
class Page:
    """A batch of changes plus the cursor to resume from."""

    records: tuple[SourceRecord, ...]
    cursor: str | None
    has_more: bool = False


@runtime_checkable
class Connector(Protocol):
    @property
    def name(self) -> str: ...

    def fetch(self, cursor: str | None) -> Page:
        """Artifacts created or modified since `cursor`."""
        ...

    def enumerate_ids(self) -> set[str]:
        """Every external id the source currently holds.

        Used for delete detection. Expensive by nature — a full enumeration —
        which is why deletion freshness is an SLA rather than immediate.
        """
        ...

    def grants(self) -> Iterator[Grant]:
        """Current membership, for mirroring into the grant table."""
        ...


@dataclass
class SyncState:
    """Per-connector cursor and last-seen id set.

    ``seen`` is what makes delete detection possible: the ids present at the
    end of the previous sync. Anything in ``seen`` and absent from the current
    enumeration was deleted upstream.
    """

    connector: str
    cursor: str | None = None
    seen: set[str] = field(default_factory=set)
    last_synced_at: str | None = None

    @classmethod
    def load(cls, backend: StoreBackend, connector: str) -> SyncState:
        raw = backend.read_text(f"{SYNC_PREFIX}/{connector}.json")
        if raw is None:
            return cls(connector=connector)
        data = json.loads(raw)
        return cls(
            connector=connector,
            cursor=data.get("cursor"),
            seen=set(data.get("seen", [])),
            last_synced_at=data.get("last_synced_at"),
        )

    def save(self, backend: StoreBackend, *, now: datetime | None = None) -> None:
        # A wall-clock timestamp is fine here — this file is workflow state, not
        # canonical content, and is excluded from the determinism contract.
        stamp = (now or datetime.now(UTC)).isoformat()
        backend.write_text(
            f"{SYNC_PREFIX}/{self.connector}.json",
            json.dumps(
                {
                    "connector": self.connector,
                    "cursor": self.cursor,
                    "seen": sorted(self.seen),
                    "last_synced_at": stamp,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        self.last_synced_at = stamp
