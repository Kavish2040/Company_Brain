"""Web OAuth2 flow for per-user Gmail authorization.

Handles the standard web-app redirect flow (not the CLI's loopback), with
in-memory session tracking keyed by a random session ID (HttpOnly cookie).
"""

import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from fastapi import APIRouter, Cookie, HTTPException
from fastapi.responses import RedirectResponse

from company_brain.connectors.google_auth import (
    OAuthError,
    TokenStore,
    build_authorization_url,
    exchange_code_for_tokens,
    generate_pkce_and_state,
)

router = APIRouter(tags=["gmail"])

_SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

_oauth_sessions: dict[str, dict[str, Any]] = {}


@router.get("/oauth/start")
def oauth_start() -> RedirectResponse:
    """Initiate the OAuth flow: generate and store PKCE/state, redirect to Google."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="GOOGLE_CLIENT_ID not set — see .env.example",
        )

    state, code_verifier, code_challenge = generate_pkce_and_state()
    session_id = secrets.token_urlsafe(32)

    _oauth_sessions[session_id] = {
        "state": state,
        "code_verifier": code_verifier,
        "created_at": datetime.now(UTC),
    }

    redirect_uri = "http://localhost:8000/api/gmail/oauth/callback"
    auth_url = build_authorization_url(client_id, redirect_uri, _SCOPES, state, code_challenge)

    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        "gmail_session",
        session_id,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600,
    )

    return response


@router.get("/oauth/callback")
def oauth_callback(
    code: str,
    state: str,
    gmail_session: str | None = Cookie(None),
    error: str | None = None,
) -> RedirectResponse:
    """Handle the OAuth callback: exchange code for tokens, fetch account email."""
    if error:
        raise HTTPException(status_code=400, detail=f"authorization denied: {error}")

    if not gmail_session or gmail_session not in _oauth_sessions:
        raise HTTPException(status_code=400, detail="invalid or missing session")

    session_data = _oauth_sessions[gmail_session]
    stored_state = session_data["state"]
    code_verifier = session_data["code_verifier"]

    if state != stored_state:
        raise HTTPException(status_code=400, detail="state mismatch — possible CSRF")

    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set",
        )

    try:
        redirect_uri = "http://localhost:8000/api/gmail/oauth/callback"
        tokens = exchange_code_for_tokens(client_id, client_secret, code, redirect_uri, code_verifier)
        access_token = tokens["access_token"]
    except OAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        resp = httpx.get(
            _USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        resp.raise_for_status()
        userinfo = resp.json()
        email = userinfo.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="no email in userinfo")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=400, detail=f"userinfo fetch failed: {exc}")

    try:
        account_key = f"gmail:{email}"
        TokenStore.save(account_key, {"refresh_token": tokens["refresh_token"]})

        _oauth_sessions[gmail_session]["account_key"] = account_key
        _oauth_sessions[gmail_session]["authorized_at"] = datetime.now(UTC)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"token store failed: {exc}")

    return RedirectResponse(url="http://localhost:5173", status_code=302)


@router.post("/oauth/logout")
def oauth_logout(
    response: Response,
    gmail_session: str | None = Cookie(None),
) -> dict[str, str]:
    """Revoke the session and delete the stored refresh token."""
    if gmail_session and gmail_session in _oauth_sessions:
        session_data = _oauth_sessions[gmail_session]
        if "account_key" in session_data:
            try:
                TokenStore.delete(session_data["account_key"])
            except Exception:
                pass
        del _oauth_sessions[gmail_session]

    response.delete_cookie("gmail_session")
    return {"status": "logged_out"}


def get_account_key_for_session(gmail_session: str | None) -> str | None:
    """Resolve the account key (gmail:<email>) for a session cookie."""
    if not gmail_session or gmail_session not in _oauth_sessions:
        return None
    session_data = _oauth_sessions[gmail_session]
    if "account_key" not in session_data:
        return None
    created_at = session_data.get("created_at")
    if created_at and datetime.now(UTC) - created_at > timedelta(hours=1):
        del _oauth_sessions[gmail_session]
        return None
    return session_data["account_key"]


def cleanup_expired_sessions() -> None:
    """Clean up OAuth sessions older than 1 hour."""
    now = datetime.now(UTC)
    expired = [
        sid
        for sid, data in _oauth_sessions.items()
        if now - data.get("created_at", now) > timedelta(hours=1)
    ]
    for sid in expired:
        del _oauth_sessions[sid]
