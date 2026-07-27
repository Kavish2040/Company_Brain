"""Real Google Drive API transport implementing DriveTransport protocol.

Uses httpx for REST calls. Handles pagination, folder scoping, and exact error mapping
(no status code remapping — 403 stays 403, 404 stays 404) to preserve the critical
403-vs-404 distinction in delete classification (ARCHITECTURE §9.3).

Folder scoping: list_files() and permissions() are filtered server-side via
`q="... and '<folder_id>' in parents"`. changes() is filtered client-side after the
API call (Drive's Changes API has no folder param). get_file() is unscoped — needed
by classify_departure() to correctly identify files moved out of the synced folder.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from company_brain.connectors.drive import DriveApiError
from company_brain.connectors.google_auth import GoogleOAuthCredentials


@dataclass
class GoogleDriveTransport:
    """Real Google Drive REST transport.

    scope_folder_id: the folder ID to sync (direct children only, non-recursive).
      No default — scoping is required, matching the CLI's --folder mandate.
    """

    credentials: GoogleOAuthCredentials
    scope_folder_id: str
    client: httpx.Client | None = None

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = httpx.Client(timeout=30, follow_redirects=True)

    def start_page_token(self) -> str:
        """Get the starting page token for changes.list (used on cold start)."""
        resp = self._call(
            "GET", "/drive/v3/changes/startPageToken", params={"supportsAllDrives": "true"}
        )
        return resp.get("startPageToken", "")

    def changes(self, page_token: str) -> dict[str, Any]:
        """Fetch a single page of changes since page_token.

        Client-side filters by folder ID — removes entries whose file's parents
        don't include the scope folder. Bare `removed: true` with no file passes
        through (harmless — classify_departure() only invokes for files we've
        previously seen in scope).
        """
        params = {
            "pageToken": page_token,
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true",
            "includeRemoved": "true",
            "pageSize": "100",
            "fields": (
                "nextPageToken,newStartPageToken,"
                "changes(fileId,removed,file(id,name,mimeType,version,modifiedTime,"
                "createdTime,trashed,parents,driveId))"
            ),
        }
        result = self._call("GET", "/drive/v3/changes", params=params)

        # Client-side filter: keep changes where file parents include the scope folder.
        # Files with no/missing parents are filtered (likely shared-drive roots).
        filtered_changes = []
        for change in result.get("changes", []):
            if change.get("removed") and change.get("file") is None:
                # Bare removal with no file — pass through (no parents to check).
                filtered_changes.append(change)
            elif change.get("file") and isinstance(change.get("file"), dict):
                file_obj = change["file"]
                parents = file_obj.get("parents", [])
                if isinstance(parents, list) and self.scope_folder_id in parents:
                    filtered_changes.append(change)
            # Else: filtered out (not in scope or no file data).

        result["changes"] = filtered_changes
        return result

    def list_files(self) -> list[dict[str, Any]]:
        """Fetch all live, non-trashed files in the scope folder (paginated, flattened).

        Server-side filter via q parameter.
        """
        all_files: list[dict[str, Any]] = []
        page_token: str | None = None

        while True:
            params: dict[str, str] = {
                "q": f"trashed=false and '{self.scope_folder_id}' in parents",
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
                "pageSize": "1000",
                "fields": (
                    "nextPageToken,"
                    "files(id,name,mimeType,version,modifiedTime,createdTime,trashed,parents,driveId)"
                ),
            }
            if page_token:
                params["pageToken"] = page_token

            result = self._call("GET", "/drive/v3/files", params=params)
            all_files.extend(result.get("files", []))

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return all_files

    def get_file(self, file_id: str) -> dict[str, Any]:
        """Get metadata for a single file by ID (unscoped).

        Used only by classify_departure(). Unscoped so a file that moved out of
        the synced folder can still be reached and classified as ACCESS_LOST, not
        DELETED.

        Raises DriveApiError with status 404 for "file gone" OR "you can't see
        it anymore" (Drive returns 404 for both); 403 for explicit unshare.
        """
        params = {
            "supportsAllDrives": "true",
            "fields": (
                "id,name,mimeType,version,modifiedTime,createdTime,trashed,parents,driveId"
            ),
        }
        return self._call("GET", f"/drive/v3/files/{file_id}", params=params)

    def download(self, file_id: str, export_mime: str | None) -> bytes:
        """Download a file's content (direct or exported).

        export_mime: None → download as-is (?alt=media). A mime type (e.g.
          "text/markdown") → export to that format (/export?mimeType=...).
        """
        if export_mime:
            url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export"
            params = {"mimeType": export_mime, "supportsAllDrives": "true"}
            # Use lower-level _call_raw for downloads (returns bytes, not JSON).
            return self._call_raw("GET", url, params=params)
        else:
            url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
            params = {"alt": "media", "supportsAllDrives": "true"}
            return self._call_raw("GET", url, params=params)

    def permissions(self, file_id: str) -> list[dict[str, Any]]:
        """Fetch all permissions for a file (paginated, flattened).

        Only called for files list_files() returned, so implicitly in-scope.
        """
        all_perms: list[dict[str, Any]] = []
        page_token: str | None = None

        while True:
            params: dict[str, str] = {
                "supportsAllDrives": "true",
                "pageSize": "100",
                "fields": "nextPageToken,permissions(id,type,emailAddress,domain,role)",
            }
            if page_token:
                params["pageToken"] = page_token

            result = self._call("GET", f"/drive/v3/files/{file_id}/permissions", params=params)
            all_perms.extend(result.get("permissions", []))

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return all_perms

    # ---- Internal ----

    def _call(
        self, method: str, path: str, *, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Make a JSON REST call, returning the parsed response body.

        Raises DriveApiError on non-2xx. On a 401, forces a bearer token refresh
        and retries exactly once; any other non-2xx (or a repeated 401) raises
        immediately with no remapping.
        """
        assert self.client is not None
        url = f"https://www.googleapis.com{path}"
        headers = {"Authorization": f"Bearer {self.credentials.bearer_token()}"}

        try:
            resp = self.client.request(method, url, params=params, headers=headers)
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            raise RuntimeError(f"drive api request failed: {exc.__class__.__name__}") from exc

        if resp.status_code == 401:
            # Force refresh and retry once.
            self.credentials._refresh_access_token(force=True)
            headers["Authorization"] = f"Bearer {self.credentials.bearer_token()}"
            try:
                resp = self.client.request(method, url, params=params, headers=headers)
            except (httpx.RequestError, httpx.TimeoutException) as exc:
                raise RuntimeError(f"drive api request failed after refresh: {exc}") from exc

        if resp.status_code >= 400:
            # Parse error message if JSON; otherwise use raw text.
            message = ""
            try:
                error_body = resp.json()
                message = error_body.get("error", {}).get("message", "")
            except Exception:
                message = resp.text[:200] if resp.text else ""

            raise DriveApiError(status=resp.status_code, message=message)

        return resp.json()

    def _call_raw(
        self, method: str, url: str, *, params: dict[str, str] | None = None
    ) -> bytes:
        """Make a REST call, returning the raw response bytes.

        Used for downloads (alt=media, exports). Same error handling and retry
        logic as _call().
        """
        assert self.client is not None
        headers = {"Authorization": f"Bearer {self.credentials.bearer_token()}"}

        try:
            resp = self.client.request(method, url, params=params, headers=headers)
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            raise RuntimeError(f"drive api request failed: {exc.__class__.__name__}") from exc

        if resp.status_code == 401:
            self.credentials._refresh_access_token(force=True)
            headers["Authorization"] = f"Bearer {self.credentials.bearer_token()}"
            try:
                resp = self.client.request(method, url, params=params, headers=headers)
            except (httpx.RequestError, httpx.TimeoutException) as exc:
                raise RuntimeError(f"drive api request failed after refresh: {exc}") from exc

        if resp.status_code >= 400:
            raise DriveApiError(status=resp.status_code, message=resp.text[:200])

        return resp.content
