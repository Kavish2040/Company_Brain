"""Gmail API client via httpx with incremental sync via history.list."""

from typing import Any

import httpx

from company_brain.connectors.google_auth import GoogleOAuthCredentials


class GmailClient:
    """Gmail API access via incremental sync (history.list) with fallback to full list."""

    def __init__(self, credentials: GoogleOAuthCredentials):
        self.credentials = credentials

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.credentials.bearer_token()}"}

    def get_history_id(self) -> str | None:
        """Fetch the current historyId from the user's profile."""
        url = "https://www.googleapis.com/gmail/v1/users/me/profile"
        try:
            resp = httpx.get(url, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            return resp.json().get("historyId")
        except httpx.HTTPError:
            return None

    def get_history(self, history_id: str, max_results: int = 100) -> dict[str, Any]:
        """Fetch messages from history since the given historyId.

        Returns a dict with:
        - messages: list of message dicts with id, threadId, historyId
        - history: list of history dicts with each containing messages/labels/etc
        - historyId: the new historyId to store for next sync
        """
        url = "https://www.googleapis.com/gmail/v1/users/me/history"
        params = {
            "startHistoryId": history_id,
            "maxResults": max_results,
            "historyTypes": "messageAdded",
        }
        try:
            resp = httpx.get(url, params=params, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            result = resp.json()
            return result
        except httpx.HTTPError as exc:
            raise RuntimeError(f"history.list failed: {exc}")

    def list_messages(
        self,
        q: str = "in:inbox",
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch recent messages via full list (used on first sync or if historyId expired).

        Returns a list of message metadata dicts (id, threadId, labelIds, etc).
        """
        url = "https://www.googleapis.com/gmail/v1/users/me/messages"
        params = {
            "q": q,
            "maxResults": max_results,
        }
        try:
            resp = httpx.get(url, params=params, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("messages", [])
        except httpx.HTTPError as exc:
            raise RuntimeError(f"messages.list failed: {exc}")

    def get_message(self, message_id: str, format: str = "minimal") -> dict[str, Any]:
        """Fetch a single message's metadata and snippet.

        Format can be "minimal" (id, threadId, labelIds, snippet, sizeEstimate)
        or "full" (all of above plus body).
        """
        url = f"https://www.googleapis.com/gmail/v1/users/me/messages/{message_id}"
        params = {"format": format}
        try:
            resp = httpx.get(url, params=params, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"get_message {message_id} failed: {exc}")

    def list_labels(self) -> dict[str, str]:
        """Fetch all labels and return a map of labelId -> labelName."""
        url = "https://www.googleapis.com/gmail/v1/users/me/labels"
        try:
            resp = httpx.get(url, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            data = resp.json()
            labels = {}
            for label_obj in data.get("labels", []):
                labels[label_obj["id"]] = label_obj["name"]
            return labels
        except httpx.HTTPError as exc:
            raise RuntimeError(f"labels.list failed: {exc}")
