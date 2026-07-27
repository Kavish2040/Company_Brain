"""FastAPI routes for Gmail triage: /status, /triage, /refresh."""

import email.utils
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Cookie, HTTPException

from company_brain.connectors.google_auth import GoogleOAuthCredentials, OAuthError, TokenStore
from company_brain.gmail_triage.classify import classify_message
from company_brain.gmail_triage.client import GmailClient
from company_brain.gmail_triage.oauth import get_account_key_for_session
from company_brain.gmail_triage.state import Message, StateStore, TriageState, EmailBucket


router = APIRouter(tags=["gmail"], prefix="/api/gmail")


def _extract_date(headers: list[dict[str, str]]) -> str:
    """Extract Date header and return ISO format string."""
    for header in headers:
        if header.get("name", "").lower() == "date":
            date_str = header.get("value", "")
            try:
                dt = email.utils.parsedate_to_datetime(date_str)
                return dt.isoformat()
            except (TypeError, ValueError):
                return datetime.now(UTC).isoformat()
    return datetime.now(UTC).isoformat()


def _extract_headers(message_data: dict[str, Any], keys: list[str]) -> dict[str, str]:
    """Extract specific headers from a message."""
    headers = message_data.get("payload", {}).get("headers", [])
    result = {}
    for key in keys:
        for header in headers:
            if header.get("name", "").lower() == key.lower():
                result[key] = header.get("value", "")
                break
    return result


@router.get("/status")
def get_status(gmail_session: str | None = Cookie(None)) -> dict[str, Any]:
    """Check if the current session has a linked Gmail account."""
    account_key = get_account_key_for_session(gmail_session)
    if not account_key:
        return {"linked": False, "email": None, "lastRefreshed": None}

    email_addr = account_key.split(":", 1)[1] if ":" in account_key else None
    state = StateStore.load(account_key)
    return {
        "linked": True,
        "email": email_addr,
        "lastRefreshed": state.last_refreshed_at if state else None,
    }


@router.get("/triage")
def get_triage(
    gmail_session: str | None = Cookie(None),
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Fetch triaged inbox: cached if <15min old, re-fetched if stale or forced."""
    account_key = get_account_key_for_session(gmail_session)
    if not account_key:
        raise HTTPException(status_code=401, detail="no active Gmail session")

    try:
        token_data = TokenStore.load(account_key)
        if not token_data or "refresh_token" not in token_data:
            raise HTTPException(status_code=401, detail="refresh token not found")

        creds = GoogleOAuthCredentials(
            client_id="",
            client_secret="",
            refresh_token=token_data["refresh_token"],
        )
    except OAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    state = StateStore.load(account_key) or TriageState.default(account_key)

    if not force_refresh and not state.is_stale(15):
        return {
            "email": account_key.split(":", 1)[1],
            "lastRefreshed": state.last_refreshed_at,
            "buckets": {
                bucket: [msg.to_dict() for msg in messages]
                for bucket, messages in state.messages.items()
            },
        }

    try:
        client = GmailClient(creds)
        label_map = client.list_labels()

        new_messages: dict[EmailBucket, list[Message]] = {bucket: [] for bucket in EmailBucket}

        if state.last_history_id:
            try:
                history_data = client.get_history(state.last_history_id, max_results=50)
                message_ids = set()
                for history_entry in history_data.get("history", []):
                    for msg_dict in history_entry.get("messages", []):
                        message_ids.add(msg_dict["id"])

                for msg_id in list(message_ids)[:10]:
                    msg_data = client.get_message(msg_id, format="full")
                    label_ids = msg_data.get("labelIds", [])
                    label_names = [label_map.get(lid, lid) for lid in label_ids]
                    starred = any(name == "STARRED" for name in label_names)

                    headers = _extract_headers(msg_data, ["Subject", "From", "Date"])
                    subject = headers.get("Subject", "(no subject)")
                    from_addr = headers.get("From", "(unknown)")
                    received_at = _extract_date(msg_data.get("payload", {}).get("headers", []))

                    bucket = classify_message(label_names, starred)
                    snippet = msg_data.get("snippet", "")

                    msg = Message(
                        id=msg_id,
                        thread_id=msg_data.get("threadId", ""),
                        subject=subject,
                        from_=from_addr,
                        snippet=snippet,
                        received_at=received_at,
                        bucket=bucket,
                        labels=label_names,
                    )
                    new_messages[bucket].append(msg)

                state.last_history_id = history_data.get("historyId")
            except RuntimeError:
                history_id = client.get_history_id()
                if history_id:
                    state.last_history_id = history_id
                else:
                    state.last_history_id = None
        else:
            history_id = client.get_history_id()
            state.last_history_id = history_id

        if not new_messages or all(not msgs for msgs in new_messages.values()):
            msg_list = client.list_messages(q="in:inbox", max_results=10)
            for msg_metadata in msg_list:
                msg_id = msg_metadata["id"]
                msg_data = client.get_message(msg_id, format="full")
                label_ids = msg_data.get("labelIds", [])
                label_names = [label_map.get(lid, lid) for lid in label_ids]
                starred = any(name == "STARRED" for name in label_names)

                headers = _extract_headers(msg_data, ["Subject", "From", "Date"])
                subject = headers.get("Subject", "(no subject)")
                from_addr = headers.get("From", "(unknown)")
                received_at = _extract_date(msg_data.get("payload", {}).get("headers", []))

                bucket = classify_message(label_names, starred)
                snippet = msg_data.get("snippet", "")

                msg = Message(
                    id=msg_id,
                    thread_id=msg_data.get("threadId", ""),
                    subject=subject,
                    from_=from_addr,
                    snippet=snippet,
                    received_at=received_at,
                    bucket=bucket,
                    labels=label_names,
                )
                new_messages[bucket].append(msg)

        state.messages = new_messages
        state.last_refreshed_at = datetime.now(UTC).isoformat()
        StateStore.save(state)

    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=f"Gmail fetch failed: {exc}")

    return {
        "email": account_key.split(":", 1)[1],
        "lastRefreshed": state.last_refreshed_at,
        "buckets": {
            bucket: [msg.to_dict() for msg in messages]
            for bucket, messages in state.messages.items()
        },
    }
