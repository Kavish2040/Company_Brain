"""Tests for Google Drive real transport (DriveTransport protocol)."""

from __future__ import annotations

from typing import Any
from unittest import mock

import httpx
import pytest

from company_brain.connectors.drive import DriveApiError
from company_brain.connectors.gdrive_transport import GoogleDriveTransport


class StubCredentials:
    """Stub credentials for testing (no actual OAuth)."""

    def bearer_token(self) -> str:
        return "test-access-token"

    def _refresh_access_token(self, *, force: bool = False) -> None:
        pass  # No-op for tests


@pytest.fixture
def stub_creds() -> StubCredentials:
    """Stub credentials fixture."""
    return StubCredentials()


@pytest.fixture
def transport(stub_creds: StubCredentials) -> GoogleDriveTransport:
    """GoogleDriveTransport with mock HTTP client."""
    transport = GoogleDriveTransport(
        credentials=stub_creds,
        scope_folder_id="folder-123",
        client=httpx.Client(),  # Will be mocked per test
    )
    return transport


class TestErrorMapping:
    """Exact status code mapping (403 stays 403, 404 stays 404)."""

    def test_get_file_404_raises_drivapieerror_404(self, transport: GoogleDriveTransport) -> None:
        """get_file on a 404 response raises DriveApiError with status 404."""

        def mock_request(*args: Any, **kwargs: Any) -> httpx.Response:
            return httpx.Response(404, json={"error": {"message": "File not found"}})

        transport.client.request = mock_request  # type: ignore

        with pytest.raises(DriveApiError) as exc_info:
            transport.get_file("file-404")

        assert exc_info.value.status == 404

    def test_get_file_403_raises_drivapieerror_403(self, transport: GoogleDriveTransport) -> None:
        """get_file on a 403 response raises DriveApiError with status 403."""

        def mock_request(*args: Any, **kwargs: Any) -> httpx.Response:
            return httpx.Response(403, json={"error": {"message": "Permission denied"}})

        transport.client.request = mock_request  # type: ignore

        with pytest.raises(DriveApiError) as exc_info:
            transport.get_file("file-403")

        assert exc_info.value.status == 403

    def test_401_triggers_refresh_retry(self, transport: GoogleDriveTransport, stub_creds: StubCredentials) -> None:
        """401 forces a token refresh and retries once."""
        call_count = [0]

        def mock_request(*args: Any, **kwargs: Any) -> httpx.Response:
            call_count[0] += 1
            if call_count[0] == 1:
                return httpx.Response(401)
            # Second call (after refresh) succeeds.
            return httpx.Response(200, json={"id": "file-1"})

        transport.client.request = mock_request  # type: ignore
        stub_creds._refresh_access_token = mock.Mock()  # Track that refresh was called

        result = transport.get_file("file-1")
        assert result["id"] == "file-1"
        stub_creds._refresh_access_token.assert_called_once_with(force=True)
        assert call_count[0] == 2  # Two requests made

    def test_401_after_refresh_still_raises(self, transport: GoogleDriveTransport, stub_creds: StubCredentials) -> None:
        """401 after refresh is raised unmodified (never coerced to 403/404)."""

        def mock_request(*args: Any, **kwargs: Any) -> httpx.Response:
            return httpx.Response(401)

        transport.client.request = mock_request  # type: ignore

        with pytest.raises(DriveApiError) as exc_info:
            transport.get_file("file-1")

        assert exc_info.value.status == 401


class TestListFiles:
    """File enumeration with server-side scope filtering."""

    def test_list_files_sends_folder_filter(self, transport: GoogleDriveTransport) -> None:
        """list_files sends q parameter with folder filter."""
        requests_made = []

        def mock_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
            requests_made.append((method, url, kwargs.get("params")))
            return httpx.Response(200, json={"files": []})

        transport.client.request = mock_request  # type: ignore
        transport.list_files()

        assert len(requests_made) == 1
        _, _, params = requests_made[0]
        assert "folder-123" in params["q"]
        assert "trashed=false" in params["q"]

    def test_list_files_flattens_pagination(self, transport: GoogleDriveTransport) -> None:
        """list_files flattens multiple pages into one list."""
        responses = [
            httpx.Response(
                200,
                json={
                    "files": [{"id": "file-1"}, {"id": "file-2"}],
                    "nextPageToken": "token-page-2",
                },
            ),
            httpx.Response(
                200,
                json={
                    "files": [{"id": "file-3"}],
                    "nextPageToken": None,
                },
            ),
        ]
        response_iter = iter(responses)

        def mock_request(*args: Any, **kwargs: Any) -> httpx.Response:
            return next(response_iter)

        transport.client.request = mock_request  # type: ignore

        files = transport.list_files()
        assert len(files) == 3
        assert [f["id"] for f in files] == ["file-1", "file-2", "file-3"]


class TestChanges:
    """Changes feed with client-side scope filtering."""

    def test_changes_is_single_page_passthrough(self, transport: GoogleDriveTransport) -> None:
        """changes returns the API response as-is (no internal pagination loop)."""
        response_data = {
            "changes": [{"fileId": "f1", "file": {"id": "f1", "parents": ["folder-123"]}}],
            "nextPageToken": "token-page-2",
        }

        def mock_request(*args: Any, **kwargs: Any) -> httpx.Response:
            return httpx.Response(200, json=response_data)

        transport.client.request = mock_request  # type: ignore

        result = transport.changes("start-token")
        assert "nextPageToken" in result
        assert result["nextPageToken"] == "token-page-2"

    def test_changes_filters_out_of_scope_files(self, transport: GoogleDriveTransport) -> None:
        """changes drops entries whose file's parents don't include the scope folder."""
        response_data = {
            "changes": [
                {"fileId": "f1", "file": {"id": "f1", "parents": ["folder-123"]}},  # In scope
                {"fileId": "f2", "file": {"id": "f2", "parents": ["other-folder"]}},  # Out of scope
                {"fileId": "f3", "removed": True},  # Bare removal (no file) — pass through
            ],
            "newStartPageToken": "token-3",
        }

        def mock_request(*args: Any, **kwargs: Any) -> httpx.Response:
            return httpx.Response(200, json=response_data)

        transport.client.request = mock_request  # type: ignore

        result = transport.changes("token")
        changes = result["changes"]
        assert len(changes) == 2
        assert changes[0]["fileId"] == "f1"
        assert changes[1]["fileId"] == "f3"


class TestPermissions:
    """Permission enumeration with pagination flattening."""

    def test_permissions_flattens_pagination(self, transport: GoogleDriveTransport) -> None:
        """permissions flattens multiple pages."""
        responses = [
            httpx.Response(
                200,
                json={
                    "permissions": [{"id": "p1", "type": "user"}],
                    "nextPageToken": "token-2",
                },
            ),
            httpx.Response(
                200,
                json={
                    "permissions": [{"id": "p2", "type": "domain"}],
                    "nextPageToken": None,
                },
            ),
        ]
        response_iter = iter(responses)

        def mock_request(*args: Any, **kwargs: Any) -> httpx.Response:
            return next(response_iter)

        transport.client.request = mock_request  # type: ignore

        perms = transport.permissions("file-123")
        assert len(perms) == 2
        assert perms[0]["id"] == "p1"
        assert perms[1]["id"] == "p2"


class TestDownload:
    """File content download (direct vs. export)."""

    def test_download_direct_uses_alt_media(self, transport: GoogleDriveTransport) -> None:
        """download with no export_mime uses alt=media."""
        requests_made = []

        def mock_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
            requests_made.append((url, kwargs.get("params")))
            return httpx.Response(200, content=b"file-content")

        transport.client.request = mock_request  # type: ignore

        content = transport.download("file-123", None)
        assert content == b"file-content"
        _, params = requests_made[0]
        assert params["alt"] == "media"

    def test_download_export_uses_export_endpoint(self, transport: GoogleDriveTransport) -> None:
        """download with export_mime uses /export?mimeType=..."""
        requests_made = []

        def mock_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
            requests_made.append((url, kwargs.get("params")))
            return httpx.Response(200, content=b"exported-content")

        transport.client.request = mock_request  # type: ignore

        content = transport.download("file-123", "text/markdown")
        assert content == b"exported-content"
        url, params = requests_made[0]
        assert "/export" in url
        assert params["mimeType"] == "text/markdown"


class TestAuthorizationHeader:
    """Bearer token is sent on every request."""

    def test_bearer_token_in_headers(self, transport: GoogleDriveTransport) -> None:
        """Every request includes Authorization: Bearer header."""
        requests_made = []

        def mock_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
            requests_made.append(kwargs.get("headers"))
            return httpx.Response(200, json={})

        transport.client.request = mock_request  # type: ignore

        try:
            transport.start_page_token()
        except Exception:
            pass

        assert len(requests_made) >= 1
        headers = requests_made[0]
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-access-token"


class TestFieldsProjection:
    """Requests include only needed fields to keep responses lean."""

    def test_get_file_fields_projection(self, transport: GoogleDriveTransport) -> None:
        """get_file requests only necessary fields."""
        requests_made = []

        def mock_request(method: str, url: str, **kwargs: Any) -> httpx.Response:
            requests_made.append(kwargs.get("params"))
            return httpx.Response(200, json={"id": "f1"})

        transport.client.request = mock_request  # type: ignore

        try:
            transport.get_file("f1")
        except Exception:
            pass

        params = requests_made[0]
        fields = params["fields"]
        assert "id" in fields
        assert "mimeType" in fields
        assert "trashed" in fields
        # Shouldn't ask for file content or other unnecessary fields.
        assert "webViewLink" not in fields
        assert "description" not in fields
