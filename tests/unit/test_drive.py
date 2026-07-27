"""The Drive connector, against a fake transport.

No credentials, no network, no VCR cassettes. The whole point of the connector's
narrow transport protocol is that the interesting behaviour — which
disappearances are deletes — is testable as pure logic, because that is the
behaviour nobody can afford to get wrong twice.

The classification tests are the ones that matter. Everything else here is
plumbing; `test_a_bare_removal_is_never_a_delete` is the one standing between a
routine unshare and a purged body.
"""

from __future__ import annotations

from typing import Any

import pytest

from company_brain.connectors.base import Connector, Disappearance
from company_brain.connectors.drive import (
    CONNECTOR_NAME,
    DriveApiError,
    DriveConnector,
    DriveTransport,
    acl_ref_for,
    principal_for,
    sensitivity_for,
)
from company_brain.schemas.acl import Sensitivity

DOC_MIME = "application/vnd.google-apps.document"
FOLDER = "folder-handbooks"
GROUP = "finance-team@meridian.example"

INTERNAL = Sensitivity.INTERNAL
RESTRICTED = Sensitivity.RESTRICTED
PUBLIC = Sensitivity.PUBLIC


def file_meta(
    file_id: str,
    *,
    trashed: bool = False,
    parents: list[str] | None = None,
    drive_id: str | None = None,
    mime: str = DOC_MIME,
    version: str = "1",
) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "id": file_id,
        "name": f"{file_id}.doc",
        "mimeType": mime,
        "trashed": trashed,
        "parents": parents if parents is not None else [FOLDER],
        "version": version,
        "createdTime": "2024-05-01T09:00:00.000Z",
        "modifiedTime": "2024-05-02T10:30:00.000Z",
    }
    if drive_id:
        meta["driveId"] = drive_id
    return meta


class FakeDrive:
    """A Drive that can be trashed, purged and unshared — the three signals.

    Deliberately models the API's *refusals*, not just its successes: `get_file`
    raises 404 both for a purged file and for one we may no longer see, because
    that indistinguishability is the thing under test. A fake that returned a
    tidy "deleted" flag would test a Drive that does not exist.
    """

    def __init__(self) -> None:
        self.files: dict[str, dict[str, Any]] = {}
        self.perms: dict[str, list[dict[str, Any]]] = {}
        self.bodies: dict[str, bytes] = {}
        self.changes_pages: list[dict[str, Any]] = []
        self.unshared: set[str] = set()
        self.purged: set[str] = set()
        self.downloads: list[tuple[str, str | None]] = []

    # -- authoring the world ------------------------------------------------

    def add(
        self,
        file_id: str,
        *,
        body: bytes = b"# Handbook\n\nProcurement thresholds.\n",
        permissions: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        meta = file_meta(file_id, **kwargs)
        self.files[file_id] = meta
        self.bodies[file_id] = body
        self.perms[file_id] = (
            permissions
            if permissions is not None
            else [{"type": "group", "emailAddress": GROUP, "role": "reader"}]
        )
        return meta

    def trash(self, file_id: str) -> None:
        self.files[file_id]["trashed"] = True

    def purge(self, file_id: str) -> None:
        """Empty the trash. Drive emits no event for this; the file just 404s."""
        self.files.pop(file_id, None)
        self.purged.add(file_id)

    def unshare(self, file_id: str) -> None:
        """The file is untouched; we simply stop being allowed to see it."""
        self.unshared.add(file_id)

    def queue_changes(self, *changes: dict[str, Any], token: str = "tok-2") -> None:
        self.changes_pages.append({"changes": list(changes), "newStartPageToken": token})

    # -- DriveTransport -----------------------------------------------------

    def start_page_token(self) -> str:
        return "tok-1"

    def changes(self, page_token: str) -> dict[str, Any]:
        if self.changes_pages:
            return self.changes_pages.pop(0)
        return {"changes": [], "newStartPageToken": page_token}

    def list_files(self) -> list[dict[str, Any]]:
        return [
            meta
            for fid, meta in sorted(self.files.items())
            if fid not in self.unshared and not meta.get("trashed")
        ]

    def get_file(self, file_id: str) -> dict[str, Any]:
        if file_id in self.unshared:
            # Drive will not confirm existence to someone without access.
            raise DriveApiError(404, "File not found")
        if file_id not in self.files:
            raise DriveApiError(404, "File not found")
        return self.files[file_id]

    def download(self, file_id: str, export_mime: str | None) -> bytes:
        self.downloads.append((file_id, export_mime))
        return self.bodies[file_id]

    def permissions(self, file_id: str) -> list[dict[str, Any]]:
        return self.perms.get(file_id, [])


@pytest.fixture
def drive() -> FakeDrive:
    return FakeDrive()


@pytest.fixture
def connector(drive: FakeDrive) -> DriveConnector:
    return DriveConnector(drive)


def change(file_id: str, meta: dict[str, Any] | None = None, *, removed: bool = False) -> dict:
    entry: dict[str, Any] = {"fileId": file_id, "removed": removed}
    if meta is not None:
        entry["file"] = meta
    return entry


class TestProtocolConformance:
    def test_the_connector_satisfies_the_protocol(self, connector: DriveConnector) -> None:
        assert isinstance(connector, Connector)

    def test_the_fake_satisfies_the_transport(self, drive: FakeDrive) -> None:
        """If the fake drifts from the real surface, these tests stop meaning
        anything — so the shape is asserted, not assumed."""
        assert isinstance(drive, DriveTransport)


class TestDisappearanceIsClassifiedNotGuessed:
    """The three signals, plus the one that must stay ambiguous."""

    def test_trashed_is_recoverable_so_the_body_is_retained(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")
        drive.trash("f1")

        assert connector.classify_departure("f1") is Disappearance.TRASHED

    def test_a_trashed_file_leaves_enumeration_immediately(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """It must depart now — a trashed doc should not answer questions —
        even though its body is kept in case it comes back."""
        drive.add("f1")
        assert connector.enumerate_ids() == {"f1"}
        drive.trash("f1")
        assert connector.enumerate_ids() == set()

    def test_a_purge_after_a_known_trash_is_a_real_delete(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """The only evidence of a permanent delete Drive ever gives: we watched
        it enter the trash, and now it is gone."""
        drive.add("f1")
        drive.queue_changes(change("f1", file_meta("f1", trashed=True)))
        connector.fetch(None)

        drive.purge("f1")

        assert connector.classify_departure("f1") is Disappearance.DELETED

    def test_a_bare_removal_is_never_a_delete(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """The trap. `removed: true` with no file attached means deletion OR
        loss of access, and Drive will not say which. Purging here destroys a
        document that still exists upstream."""
        drive.add("f1")
        drive.queue_changes(change("f1", removed=True))
        connector.fetch(None)

        drive.unshare("f1")

        assert connector.classify_departure("f1") is Disappearance.UNKNOWN

    def test_an_unshare_is_a_grant_change_not_a_delete(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")
        drive.unshare("f1")

        assert connector.classify_departure("f1") is not Disappearance.DELETED

    def test_an_explicit_403_is_access_lost(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")

        def forbidden(file_id: str) -> dict[str, Any]:
            raise DriveApiError(403, "insufficientFilePermissions")

        drive.get_file = forbidden  # type: ignore[method-assign]
        assert connector.classify_departure("f1") is Disappearance.ACCESS_LOST

    def test_a_file_that_merely_left_scope_is_not_a_delete(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """Still readable, not trashed: it moved out of the synced folder. That
        is not a disappearance we may act destructively on."""
        drive.add("f1", parents=["some-other-folder"])
        assert connector.classify_departure("f1") is Disappearance.ACCESS_LOST

    def test_a_transport_failure_is_not_evidence(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """A 500 or a dropped connection says nothing about the file. Reporting
        a delete because the network blinked is the worst possible trade."""

        def exploding(file_id: str) -> dict[str, Any]:
            raise DriveApiError(503, "backendError")

        drive.get_file = exploding  # type: ignore[method-assign]
        assert connector.classify_departure("f1") is Disappearance.UNKNOWN

    def test_a_restore_from_trash_forgets_the_trash_observation(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """Otherwise a file that was trashed, restored, then unshared months
        later would be read as a purge — and purged."""
        drive.add("f1")
        drive.queue_changes(change("f1", file_meta("f1", trashed=True)))
        connector.fetch(None)
        drive.queue_changes(change("f1", file_meta("f1", trashed=False)))
        connector.fetch("tok-2")

        drive.unshare("f1")

        assert connector.classify_departure("f1") is Disappearance.UNKNOWN

    def test_losing_the_trash_memory_degrades_to_safe_not_destructive(
        self, drive: FakeDrive
    ) -> None:
        """The trash set is in-process. A restart must lose it *safely*: a purge
        we never watched happen classifies as UNKNOWN, not DELETED."""
        drive.add("f1")
        drive.trash("f1")
        drive.purge("f1")

        restarted = DriveConnector(drive)  # no memory of the trashing
        assert restarted.classify_departure("f1") is Disappearance.UNKNOWN


class TestRetentionOptIn:
    def test_purge_on_delete_is_the_default(self, connector: DriveConnector) -> None:
        assert connector.retain_body_on_delete is False

    def test_the_opt_in_does_not_fake_a_trash_to_win_retention(self, drive: FakeDrive) -> None:
        """§14 Q3 keys retention on the delete signal, and the signal must stay
        truthful. A purged file reported as TRASHED would write "moved to trash"
        into the tombstone of a file that was destroyed.

        Consequence, stated rather than hidden: the flag is inert until
        SyncEngine consults it.
        """
        drive.add("f1")
        keeper = DriveConnector(drive, retain_body_on_delete=True)
        drive.trash("f1")
        assert keeper.classify_departure("f1") is Disappearance.TRASHED

        drive.purge("f1")
        assert keeper.classify_departure("f1") is Disappearance.DELETED

    def test_sensitivity_is_not_the_retention_axis(self, drive: FakeDrive) -> None:
        """A restricted file and a public one take the same path out."""
        drive.add("secret", permissions=[{"type": "user", "emailAddress": "a@b.c"}])
        drive.add("open", permissions=[{"type": "anyone"}])
        connector = DriveConnector(drive)
        drive.queue_changes(
            change("secret", file_meta("secret", trashed=True)),
            change("open", file_meta("open", trashed=True)),
        )
        connector.fetch(None)
        drive.purge("secret")
        drive.purge("open")

        assert connector.classify_departure("secret") is Disappearance.DELETED
        assert connector.classify_departure("open") is Disappearance.DELETED


class TestAclRefSurvivesMembership:
    def test_a_group_share_does_not_flatten_to_per_user_grants(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """The requirement in one test: one group, one grant. Flattening would
        make a membership edit look like mass revocation."""
        drive.add(
            "f1",
            permissions=[
                {"type": "group", "emailAddress": GROUP},
                {"type": "user", "emailAddress": "cfo@meridian.example"},
            ],
        )

        grants = list(connector.grants())
        holders = {g.principal_id for g in grants}

        assert f"group:{GROUP}" in holders
        assert len([g for g in grants if g.principal_id.startswith("group:")]) == 1

    def test_the_ref_is_unchanged_when_membership_changes(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """The ref names the permission object, never the people in it."""
        drive.add("f1", permissions=[{"type": "group", "emailAddress": GROUP}])
        before = {g.acl_ref for g in connector.grants()}

        drive.perms["f1"] = [
            {"type": "group", "emailAddress": GROUP},
            {"type": "user", "emailAddress": "newjoiner@meridian.example"},
        ]
        after = {g.acl_ref for g in connector.grants()}

        assert before == after, "a membership edit changed the ACL ref"

    def test_a_shared_drive_governs_its_files(self) -> None:
        ref = acl_ref_for(file_meta("f1", drive_id="drive-finance"))
        assert ref == f"{CONNECTOR_NAME}:drive:drive-finance"

    def test_a_folder_governs_an_inherited_share(self) -> None:
        assert acl_ref_for(file_meta("f1")) == f"{CONNECTOR_NAME}:folder:{FOLDER}"

    def test_a_directly_shared_file_governs_itself(self) -> None:
        assert acl_ref_for(file_meta("f1", parents=[])) == f"{CONNECTOR_NAME}:file:f1"

    def test_files_in_one_folder_share_one_ref(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")
        drive.add("f2")
        assert len({g.acl_ref for g in connector.grants()}) == 1

    def test_every_ref_is_a_well_formed_acl_ref(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """AclRef validates the shape; a malformed one fails at ingest, not here,
        which would be a much worse place to find out."""
        from company_brain.schemas.acl import AclRef

        drive.add("f1")
        for grant in connector.grants():
            AclRef(ref=grant.acl_ref, sensitivity=grant.sensitivity)


class TestSensitivity:
    def test_link_shared_to_anyone_is_public(self) -> None:
        assert sensitivity_for([{"type": "anyone"}]) is PUBLIC

    def test_domain_wide_is_internal(self) -> None:
        assert sensitivity_for([{"type": "domain", "domain": "meridian.example"}]) is INTERNAL

    def test_named_people_only_is_restricted(self) -> None:
        assert sensitivity_for([{"type": "user", "emailAddress": "a@b.c"}]) is RESTRICTED

    def test_unknown_permissions_fail_closed(self) -> None:
        """Invariant 6's posture: absence of evidence is not visibility."""
        assert sensitivity_for([]) is RESTRICTED

    def test_the_widest_share_decides(self) -> None:
        assert sensitivity_for([{"type": "user"}, {"type": "anyone"}]) is PUBLIC


class TestPrincipals:
    @pytest.mark.parametrize(
        ("permission", "expected"),
        [
            ({"type": "group", "emailAddress": GROUP}, f"group:{GROUP}"),
            ({"type": "user", "emailAddress": "a@b.c"}, "user:a@b.c"),
            ({"type": "domain", "domain": "meridian.example"}, "domain:meridian.example"),
            ({"type": "anyone"}, "anyone"),
            ({"type": "unheard-of"}, None),
        ],
    )
    def test_principal_ids_are_namespaced(
        self, permission: dict[str, Any], expected: str | None
    ) -> None:
        assert principal_for(permission) == expected


class TestFetch:
    def test_a_changed_file_becomes_a_record(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")
        drive.queue_changes(change("f1", file_meta("f1")))

        page = connector.fetch(None)

        assert len(page.records) == 1
        record = page.records[0]
        assert record.external_id == "f1"
        assert record.suffix == ".md"
        assert record.uri == "https://drive.google.com/file/d/f1"
        assert record.acl.ref == f"{CONNECTOR_NAME}:folder:{FOLDER}"

    def test_a_google_doc_is_exported_not_downloaded_raw(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")
        drive.queue_changes(change("f1", file_meta("f1")))
        connector.fetch(None)
        assert drive.downloads == [("f1", "text/markdown")]

    def test_a_pdf_is_downloaded_as_is(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1", mime="application/pdf")
        drive.queue_changes(change("f1", file_meta("f1", mime="application/pdf")))
        page = connector.fetch(None)
        assert drive.downloads == [("f1", None)]
        assert page.records[0].suffix == ".pdf"

    def test_a_format_no_normalizer_reads_is_skipped_quietly(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """Not an error and not a skip-count on every sync: a spreadsheet is a
        normal thing to have and a permanently unreadable one."""
        drive.add("f1", mime="application/vnd.google-apps.spreadsheet")
        drive.queue_changes(
            change("f1", file_meta("f1", mime="application/vnd.google-apps.spreadsheet"))
        )
        assert connector.fetch(None).records == ()

    def test_timestamps_come_from_drive_never_the_local_clock(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """Invariant 4. A local mtime would break byte-identical re-ingestion."""
        drive.add("f1")
        drive.queue_changes(change("f1", file_meta("f1")))
        record = connector.fetch(None).records[0]

        assert record.created is not None and record.modified is not None
        assert record.created.isoformat() == "2024-05-01T09:00:00+00:00"
        assert record.modified.tzinfo is not None

    def test_a_trashed_file_is_not_re_ingested_as_content(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")
        drive.queue_changes(change("f1", file_meta("f1", trashed=True)))
        assert connector.fetch(None).records == ()

    def test_a_removal_yields_no_record(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")
        drive.queue_changes(change("f1", removed=True))
        assert connector.fetch(None).records == ()

    def test_the_cursor_advances_for_the_next_sync(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")
        drive.queue_changes(change("f1", file_meta("f1")), token="tok-99")
        page = connector.fetch(None)
        assert page.cursor == "tok-99"
        assert page.has_more is False

    def test_pagination_is_reported_so_the_engine_keeps_going(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")
        drive.changes_pages.append(
            {"changes": [change("f1", file_meta("f1"))], "nextPageToken": "page-2"}
        )
        page = connector.fetch(None)
        assert page.has_more is True
        assert page.cursor == "page-2"

    def test_a_cold_start_asks_drive_where_to_begin(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        assert connector.fetch(None).cursor == "tok-1"


class TestEnumeration:
    def test_enumeration_lists_live_files_only(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        drive.add("f1")
        drive.add("f2")
        drive.trash("f2")
        assert connector.enumerate_ids() == {"f1"}

    def test_an_unshared_file_falls_out_of_enumeration(
        self, connector: DriveConnector, drive: FakeDrive
    ) -> None:
        """Which is exactly why the seen-set diff cannot be trusted on its own —
        this file is alive and well upstream."""
        drive.add("f1")
        drive.unshare("f1")
        assert connector.enumerate_ids() == set()
        assert connector.classify_departure("f1") is not Disappearance.DELETED
