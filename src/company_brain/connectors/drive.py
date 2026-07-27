"""Google Drive connector.

Drive is the first source where absence is genuinely ambiguous, and getting that
wrong is the one unrecoverable mistake in the sync path. The changes feed says so
itself: `removed` means "removed from this list of changes, **for example** by
deletion or loss of access". An enumeration diff cannot tell those apart, so this
connector does not try to guess from absence alone — it classifies from the
signals Drive actually gives (§9.3, ARCHITECTURE §14 Q3).

Three disappearances, three different outcomes:

| Signal | Meaning | `Disappearance` | Body |
|---|---|---|---|
| `trashed: true` | recoverable ~30 days | `TRASHED` | **retained** |
| gone after the trash was emptied | permanent | `DELETED` | **purged** |
| gone because it was unshared | file still exists | `ACCESS_LOST` | untouched |

The retention rule is §14 Q3 as ratified: **purge the body on delete, retain the
graph always, retain the body only under explicit per-connector opt-in.**
Sensitivity is not the axis — an internal doc and a restricted doc are both
purged on a real delete, and both retained on a trash. The axis is the connector's
delete signal, which is why `classify_departure` exists at all.

When the signals do not settle it, this returns `UNKNOWN`, which `SyncEngine`
treats as access-lost: the node stays, the body stays, and the next enumeration
gets another chance. That asymmetry is deliberate. A missed delete is a bounded
freshness-SLA problem (below). A false delete purges a body that still exists
upstream, and nothing brings it back.

## Freshness SLA

Three different clocks, because the three failures cost different amounts:

* **Edits and trashes: within 5 minutes.** `changes.list` is cheap and
  incremental, so `fetch` runs on a 5-minute schedule. A trashed file leaves
  retrieval within one cycle.
* **Permanent deletions: within 24 hours.** Detecting a purge requires a full
  `files.list` enumeration and a diff, which is O(corpus) and cannot run every
  five minutes at scale. A file whose trash was emptied may therefore keep its
  body for up to 24h after the purge. That window is the price of not purging on
  a guess.
* **Permission changes: within 5 minutes.** `grants()` is mirrored on the same
  cycle as `fetch`. Until it runs, a principal removed upstream can still
  retrieve — the leak window every mirrored-permission system has (base.py).
  Bounded and reported via `synced_at`, not eliminated.

A deletion detected late is *correct but stale*. A deletion inferred early is
*wrong and permanent*. The schedule above picks the reversible side every time.

## What this connector does not do

Group membership. A file shared to a group yields exactly one grant — for the
group principal, against the file's ACL ref — never one grant per member.
Flattening would make every membership edit look like mass revocation, and would
put Drive in the business of maintaining the directory. Expanding groups to users
is `GrantTable.add_to_group`, fed by a directory sync.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol, runtime_checkable

from company_brain.connectors.base import Disappearance, Grant, Page, SourceRecord
from company_brain.schemas.acl import AclRef, Sensitivity

CONNECTOR_NAME = "gdrive"

# Deletion detection needs a full enumeration; see the SLA above.
ENUMERATION_INTERVAL_HOURS = 24
CHANGES_INTERVAL_MINUTES = 5

# Only mime types the normalizers can actually read. A record whose suffix has no
# normalizer would be counted as a skip by SyncEngine on every single sync, which
# turns a normal condition into permanent noise — so it is filtered here.
# (suffix, export mime type or None for a direct download)
_READABLE: dict[str, tuple[str, str | None]] = {
    "application/vnd.google-apps.document": (".md", "text/markdown"),
    "application/pdf": (".pdf", None),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
        ".docx",
        None,
    ),
    "text/markdown": (".md", None),
    "text/plain": (".md", None),
}


class DriveApiError(RuntimeError):
    """A non-2xx from Drive. `status` is what carries the meaning."""

    def __init__(self, status: int, message: str = "") -> None:
        super().__init__(f"drive api {status}: {message}" if message else f"drive api {status}")
        self.status = status


@runtime_checkable
class DriveTransport(Protocol):
    """The Drive REST surface this connector uses, and nothing more.

    Narrow on purpose: it is the seam the tests replace. A fake implementing
    these six methods exercises every branch below with no credentials and no
    network, which is what keeps delete classification testable at all.
    """

    def start_page_token(self) -> str:
        """`changes.getStartPageToken` — where to resume from on a cold start."""
        ...

    def changes(self, page_token: str) -> dict[str, Any]:
        """`changes.list`. Returns `changes`, and one of `nextPageToken` /
        `newStartPageToken`."""
        ...

    def list_files(self) -> list[dict[str, Any]]:
        """`files.list` over the synced scope: live, non-trashed files only."""
        ...

    def get_file(self, file_id: str) -> dict[str, Any]:
        """`files.get`. Raises `DriveApiError` — 404 for both "gone" and
        "not allowed to know", which is the ambiguity this module is about."""
        ...

    def download(self, file_id: str, export_mime: str | None) -> bytes:
        """`files.get?alt=media`, or `files.export` when `export_mime` is set."""
        ...

    def permissions(self, file_id: str) -> list[dict[str, Any]]:
        """`permissions.list` for one file."""
        ...


def _parse_time(value: Any) -> datetime | None:
    """RFC-3339 from Drive. Never a local clock — invariant 4."""
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def acl_ref_for(meta: dict[str, Any]) -> str:
    """The permission object governing a file, not the people currently in it.

    Precedence is widest-container-first, because that is the object Drive
    actually evaluates permissions against:

    1. a shared drive — one permission set for everything inside it
    2. the parent folder — where an inherited share lives
    3. the file itself — only when it is shared directly

    None of these name a *principal*. That is the point: a group being edited,
    or a person being removed, must not change the ref, or every membership edit
    would read as the whole file being revoked and re-granted.
    """
    drive_id = meta.get("driveId")
    if isinstance(drive_id, str) and drive_id:
        return f"{CONNECTOR_NAME}:drive:{drive_id}"

    parents = meta.get("parents")
    if isinstance(parents, list) and parents and isinstance(parents[0], str):
        return f"{CONNECTOR_NAME}:folder:{parents[0]}"

    return f"{CONNECTOR_NAME}:file:{meta['id']}"


def sensitivity_for(permissions: list[dict[str, Any]]) -> Sensitivity:
    """Widest share wins, and an empty permission list is restricted.

    Fail-closed on empty matches `narrowest()`: a file we could not read the
    permissions of must not default to visible.
    """
    kinds = {p.get("type") for p in permissions}
    if "anyone" in kinds:
        return Sensitivity.PUBLIC
    if "domain" in kinds:
        return Sensitivity.INTERNAL
    return Sensitivity.RESTRICTED


def principal_for(permission: dict[str, Any]) -> str | None:
    """The grant holder, as a principal id.

    A group yields the group — one grant, stable across membership changes. A
    domain yields the domain, which is how "everyone at the company" stays one
    row instead of N.
    """
    kind = permission.get("type")
    if kind == "group":
        return f"group:{permission.get('emailAddress') or permission.get('id')}"
    if kind == "user":
        return f"user:{permission.get('emailAddress') or permission.get('id')}"
    if kind == "domain":
        return f"domain:{permission.get('domain')}"
    if kind == "anyone":
        return "anyone"
    return None


@dataclass
class DriveConnector:
    """Drive as a `Connector`.

    `retain_body_on_delete` is the §14 Q3 opt-in, per connector and off by
    default, exactly as `Disappearance.DELETED` describes it: "purge the body
    unless the connector opts into retention". Keeping a purged file's body is a
    legal and retention decision rather than a technical one, which is why it is
    explicit, per connector, and *not* keyed on sensitivity.

    It is declared here and not yet consumed: `SyncEngine._depart` hardcodes
    `retain_content=False` for DELETED and never asks the connector. Honouring
    the flag is a change in sync.py, which this connector does not own. Until
    then this is a stated policy that the pipeline ignores — false advertising if
    left silent, so it is said here and in the tests.
    """

    transport: DriveTransport
    retain_body_on_delete: bool = False

    # Files observed in the trash. This is what turns a later 404 from "cannot
    # say" into "the trash was emptied": Drive gives no purge event, so the only
    # honest evidence of a permanent delete is having watched it enter the trash
    # first. Lost on restart, and losing it is safe — it degrades to UNKNOWN.
    _trashed: set[str] = field(default_factory=set)
    # Ids the changes feed reported as `removed` with no file attached, i.e. the
    # deliberately ambiguous case.
    _removed: set[str] = field(default_factory=set)

    @property
    def name(self) -> str:
        return CONNECTOR_NAME

    # ---- content ---------------------------------------------------------

    def fetch(self, cursor: str | None) -> Page:
        """Everything that moved since `cursor`, via the changes feed.

        Also the only place trash and removal signals are observed, because the
        changes feed is the only Drive surface that reports them at all —
        `files.list` simply stops returning the file.
        """
        token = cursor or self.transport.start_page_token()
        payload = self.transport.changes(token)

        records: list[SourceRecord] = []
        for change in payload.get("changes", []):
            self._observe(change)
            meta = change.get("file")
            if change.get("removed") or not isinstance(meta, dict):
                continue
            if meta.get("trashed"):
                # Trashed files leave retrieval through the departure path, not
                # by being re-ingested as content.
                continue
            record = self._record(meta)
            if record is not None:
                records.append(record)

        next_token = payload.get("nextPageToken")
        has_more = bool(next_token)
        cursor_out = next_token or payload.get("newStartPageToken") or token
        return Page(records=tuple(records), cursor=str(cursor_out), has_more=has_more)

    def _observe(self, change: dict[str, Any]) -> None:
        """Record what a change says about existence, for later classification."""
        file_id = change.get("fileId")
        if not isinstance(file_id, str) or not file_id:
            return

        meta = change.get("file")
        if isinstance(meta, dict):
            if meta.get("trashed"):
                self._trashed.add(file_id)
            else:
                # Restored from the trash: forget it, or a later unshare would
                # be misread as a purge.
                self._trashed.discard(file_id)
                self._removed.discard(file_id)
            return

        if change.get("removed"):
            # `removed` with no file: deletion *or* loss of access, and Drive
            # will not say which. Recorded, not acted on.
            self._removed.add(file_id)

    def _record(self, meta: dict[str, Any]) -> SourceRecord | None:
        readable = _READABLE.get(str(meta.get("mimeType", "")))
        if readable is None:
            return None
        suffix, export_mime = readable

        file_id = str(meta["id"])
        raw = self.transport.download(file_id, export_mime)
        permissions = self.transport.permissions(file_id)
        parents = meta.get("parents")
        parent = parents[0] if isinstance(parents, list) and parents else ""

        return SourceRecord(
            external_id=file_id,
            # Drive's own version counter, so an unchanged file is skipped before
            # anything is hashed or extracted.
            external_version=str(meta.get("version", meta.get("modifiedTime", ""))),
            uri=f"https://drive.google.com/file/d/{file_id}",
            suffix=suffix,
            raw=raw,
            acl=AclRef(ref=acl_ref_for(meta), sensitivity=sensitivity_for(permissions)),
            path=f"{CONNECTOR_NAME}/{parent}" if parent else CONNECTOR_NAME,
            created=_parse_time(meta.get("createdTime")),
            modified=_parse_time(meta.get("modifiedTime")),
        )

    # ---- existence -------------------------------------------------------

    def enumerate_ids(self) -> set[str]:
        """Live, non-trashed files in scope.

        Full enumeration, which is why deletion freshness is 24h rather than
        immediate. Trashed files are excluded deliberately: they *should* fall
        out of the seen-set and be classified, because a trashed file must leave
        retrieval now even though its body is kept.
        """
        return {
            str(f["id"])
            for f in self.transport.list_files()
            if f.get("id") and not f.get("trashed")
        }

    def classify_departure(self, external_id: str) -> Disappearance:
        """Why did this id stop appearing? Ask Drive; never infer from absence.

        Order matters. The live probe comes first because it is the only
        statement about the file *now*; the changes feed is history, and history
        is what disambiguates a 404.
        """
        try:
            meta = self.transport.get_file(external_id)
        except DriveApiError as exc:
            return self._classify_error(external_id, exc)
        except Exception:
            # A transport failure is not evidence about the file. Say so.
            return Disappearance.UNKNOWN

        if meta.get("trashed"):
            # Recoverable for ~30 days. Tombstone, keep the body.
            self._trashed.add(external_id)
            return Disappearance.TRASHED

        # Still there, still readable: it left our enumeration scope some other
        # way — moved out of the synced folder, most likely. Whatever it was, it
        # was not a delete.
        self._trashed.discard(external_id)
        return Disappearance.ACCESS_LOST

    def _classify_error(self, external_id: str, exc: DriveApiError) -> Disappearance:
        if exc.status == 403:
            # Drive is explicit: we exist, you may not look. An unshare.
            return Disappearance.ACCESS_LOST

        if exc.status == 404:
            # The ambiguous one. Drive returns 404 both for a file that is gone
            # and for a file we are no longer allowed to know exists — it will
            # not confirm existence to someone without access.
            if external_id in self._trashed:
                # We watched it go into the trash, and now it is unreachable:
                # the trash was emptied. This is the only evidence of a purge
                # Drive ever gives, since it emits no purge event.
                #
                # This stays DELETED even when `retain_body_on_delete` is set.
                # Returning TRASHED to smuggle retention through would make the
                # tombstone read "moved to trash" about a file that was purged —
                # a false statement in the audit trail to win a body we can
                # re-fetch from nowhere anyway. The flag is a declaration; see
                # the note on it for who has to honour it.
                self._trashed.discard(external_id)
                self._removed.discard(external_id)
                return Disappearance.DELETED
            # Never seen trashed. Could be a purge we missed between syncs, could
            # be an unshare. Guessing DELETED here purges a live body, so:
            return Disappearance.UNKNOWN

        return Disappearance.UNKNOWN

    # ---- permissions -----------------------------------------------------

    def grants(self) -> Iterator[Grant]:
        """Current sharing, mirrored one row per (principal, ref).

        Emitted against the file's ACL ref — a drive, a folder, or a file — so a
        group appears once. Two files in the same folder collapse to the same
        ref, which is the intent: the ref is the permission object, not the file.
        """
        emitted: set[tuple[str, str]] = set()
        for meta in self.transport.list_files():
            if meta.get("trashed"):
                continue
            ref = acl_ref_for(meta)
            permissions = self.transport.permissions(str(meta["id"]))
            tier = sensitivity_for(permissions)
            for permission in permissions:
                principal = principal_for(permission)
                if principal is None:
                    continue
                key = (principal, ref)
                if key in emitted:
                    continue
                emitted.add(key)
                yield Grant(principal_id=principal, acl_ref=ref, sensitivity=tier)
