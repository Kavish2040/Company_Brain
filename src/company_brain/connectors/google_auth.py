"""Google OAuth for Drive and other Google APIs (read-only).

This module implements the authorized "installed app" flow (RFC 8252 loopback redirect)
for obtaining and refreshing OAuth access tokens. It's provider-agnostic so a future
Gmail connector can reuse it.

Token storage: refresh tokens are persisted to disk (mode 0600) at
~/.config/company_brain/tokens/<provider>.json, outside the repo entirely. Access
tokens (short-lived) are cached in memory only and refreshed on-demand. Never log or
raise token values (invariant 15 extended to secrets).
"""

from __future__ import annotations

import base64
import hashlib
import http.server
import json
import os
import secrets
import urllib.parse
import webbrowser
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx


class OAuthError(RuntimeError):
    """OAuth flow or credential error. Messages are always actionable."""

    pass


class TokenStore:
    """On-disk refresh-token persistence, keyed by provider name."""

    _CONFIG_DIR = (
        Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser()
        / "company_brain"
        / "tokens"
    )

    @classmethod
    def path_for(cls, provider: str) -> Path:
        """Absolute path where this provider's refresh token is stored."""
        return cls._CONFIG_DIR / f"{provider}.json"

    @classmethod
    def load(cls, provider: str) -> dict[str, Any] | None:
        """Load a refresh-token record, or None if not stored."""
        path = cls.path_for(provider)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            return None

    @classmethod
    def save(cls, provider: str, data: dict[str, Any]) -> None:
        """Persist a token record atomically (temp file + os.replace).

        Ensures directory exists with mode 0700 and file is written at mode 0600.
        """
        path = cls.path_for(provider)
        path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        # Explicitly re-chmod in case umask interfered.
        os.chmod(path.parent, 0o700)

        # Write to temp file first, then atomically replace.
        temp_path = path.parent / f".{provider}.tmp"
        temp_path.write_text(json.dumps(data, indent=2))
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, path)

    @classmethod
    def delete(cls, provider: str) -> None:
        """Delete the stored token, if it exists."""
        path = cls.path_for(provider)
        path.unlink(missing_ok=True)


@dataclass
class GoogleOAuthCredentials:
    """OAuth credentials with automatic refresh on expiry.

    Access tokens are cached in memory with a 60s safety margin; refresh tokens
    are persisted to disk (via TokenStore) and never logged.
    """

    client_id: str
    client_secret: str
    refresh_token: str
    _access_token: str | None = field(default=None, init=False, repr=False)
    _expiry: datetime | None = field(default=None, init=False, repr=False)

    @classmethod
    def load(cls, provider: str) -> GoogleOAuthCredentials:
        """Load credentials from environment variables and disk token store.

        Environment variables required:
          GOOGLE_CLIENT_ID
          GOOGLE_CLIENT_SECRET

        Refresh token is loaded from TokenStore.load(provider). If either the
        environment vars or the stored token are missing, raises OAuthError with
        an actionable message pointing at `cb auth <provider>`.
        """
        client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()

        if not client_id or not client_secret:
            raise OAuthError(
                f"GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set in environment — "
                f"see .env.example, then run `cb auth {provider}`"
            )

        token_data = TokenStore.load(provider)
        if not token_data or "refresh_token" not in token_data:
            raise OAuthError(
                f"no stored refresh token for {provider} — run `cb auth {provider}` first"
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=token_data["refresh_token"],
        )

    def bearer_token(self) -> str:
        """Return a valid access token, refreshing if necessary.

        Access tokens are cached with a 60s safety margin; a 401 on a later API
        call will trigger a forced refresh. Refresh failures raise OAuthError.
        """
        # Check if cached token is still valid (with 60s margin).
        if (
            self._access_token
            and self._expiry
            and datetime.now(UTC) < self._expiry - timedelta(seconds=60)
        ):
            return self._access_token

        self._refresh_access_token()
        return self._access_token  # type: ignore

    def _refresh_access_token(self, *, force: bool = False) -> None:
        """POST to the Google token endpoint to refresh the access token.

        If `force=True`, bypass any cached-token check. Called on init and on 401.
        """
        url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            resp = httpx.post(url, data=data, timeout=30)
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            raise OAuthError(
                f"refresh token exchange failed (network error): {exc.__class__.__name__} — "
                f"run `cb auth gdrive` again"
            ) from exc

        if resp.status_code >= 400:
            # Parse error response if possible.
            try:
                error_data = resp.json()
                error_code = error_data.get("error", "unknown_error")
                error_desc = error_data.get("error_description", "")
            except Exception:
                error_code = f"http_{resp.status_code}"
                error_desc = resp.text[:200] if resp.text else ""

            if error_code == "invalid_grant":
                raise OAuthError(
                    f"refresh token rejected (invalid_grant): {error_desc} — "
                    f"run `cb auth gdrive` again"
                )
            raise OAuthError(
                f"refresh token exchange failed ({error_code}): {error_desc} — "
                f"run `cb auth gdrive` again"
            )

        body = resp.json()
        self._access_token = body["access_token"]
        expires_in = body.get("expires_in", 3600)
        self._expiry = datetime.now(UTC) + timedelta(seconds=expires_in)


def build_authorization_url(
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    code_challenge: str,
) -> str:
    """Build the Google authorization URL for the browser redirect.

    Includes PKCE (S256) and state (CSRF) params.
    """
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)


def exchange_code_for_tokens(
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str,
    code_verifier: str,
) -> dict[str, Any]:
    """Exchange an authorization code for tokens via POST to oauth2.googleapis.com.

    Returns a dict with at least `refresh_token` and `access_token`.
    Raises OAuthError on failure.
    """
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
    }

    try:
        resp = httpx.post(url, data=data, timeout=30)
    except (httpx.RequestError, httpx.TimeoutException) as exc:
        raise OAuthError(
            f"code exchange failed (network error): {exc.__class__.__name__}"
        ) from exc

    if resp.status_code >= 400:
        try:
            error_data = resp.json()
            error_msg = error_data.get("error_description", error_data.get("error", "unknown"))
        except Exception:
            error_msg = resp.text[:200] if resp.text else f"HTTP {resp.status_code}"
        raise OAuthError(f"code exchange failed: {error_msg}")

    return resp.json()


def run_local_oauth_flow(
    client_id: str,
    client_secret: str,
    scope: str,
    provider: str,
    *,
    timeout: int = 300,
) -> GoogleOAuthCredentials:
    """Run the full OAuth installed-app flow with a loopback callback server.

    1. Generate PKCE and state params.
    2. Start an HTTP server on 127.0.0.1:0 (OS-assigned ephemeral port).
    3. Open the authorization URL in the browser (and print it as a fallback).
    4. Serve exactly one request (the redirect callback) within `timeout` seconds.
    5. Exchange the authorization code for tokens.
    6. Store the refresh token via TokenStore.
    7. Return the credentials.

    Raises OAuthError on any failure (timeout, CSRF, network, rejected grant, etc.).
    """
    # Generate PKCE and CSRF params.
    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )

    # Start the loopback server on an ephemeral port.
    handler = _make_callback_handler()
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    _, port = server.server_address
    redirect_uri = f"http://127.0.0.1:{port}/callback"

    # Build and open the authorization URL.
    auth_url = build_authorization_url(client_id, redirect_uri, scope, state, code_challenge)
    print(
        f"Opening browser for authorization...\nIf the browser doesn't open, visit: {auth_url}"
    )
    webbrowser.open(auth_url)

    # Serve the callback (exactly one request, with timeout).
    server.timeout = 1.0  # Allow checking deadline periodically.
    deadline = datetime.now(UTC) + timedelta(seconds=timeout)
    while True:
        if datetime.now(UTC) > deadline:
            server.server_close()
            raise OAuthError(
                f"no callback received within {timeout}s — check the browser window, "
                f"or your firewall for the loopback port"
            )
        server.handle_request()
        if handler.received_callback:
            break

    # Extract the callback result.
    received_code = handler.received_code
    received_state = handler.received_state
    received_error = handler.received_error

    server.server_close()

    if received_error:
        raise OAuthError(f"authorization denied: {received_error}")

    if not received_code:
        raise OAuthError("no authorization code received")

    if received_state != state:
        raise OAuthError("state mismatch — possible CSRF, aborting")

    # Exchange the code for tokens.
    tokens = exchange_code_for_tokens(
        client_id, client_secret, received_code, redirect_uri, code_verifier
    )

    # Store the refresh token.
    TokenStore.save(provider, {"refresh_token": tokens["refresh_token"]})

    return GoogleOAuthCredentials(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=tokens["refresh_token"],
    )


# Global mutable state for the callback handler (the simplest way to pass data
# from a BaseHTTPRequestHandler back to the caller, without subclassing hell).
_callback_state = {
    "received_callback": False,
    "code": None,
    "state": None,
    "error": None,
}


def _make_callback_handler() -> type[http.server.BaseHTTPRequestHandler]:
    """Create a callback handler class that records the OAuth callback parameters."""

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            """Handle GET /callback?code=...&state=..."""
            if not self.path.startswith("/callback"):
                self.send_response(404)
                self.end_headers()
                return

            # Parse query parameters.
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            _callback_state["received_callback"] = True
            _callback_state["code"] = query_params.get("code", [None])[0]
            _callback_state["state"] = query_params.get("state", [None])[0]
            _callback_state["error"] = query_params.get("error", [None])[0]

            # Send a simple response.
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = b"""
            <!DOCTYPE html>
            <html>
            <head><title>Authorization Complete</title></head>
            <body>
            <h1>Authorization Complete</h1>
            <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(html)

        def log_message(self, format: str, *args: Any) -> None:
            """Suppress default request logging (which would include the auth code)."""
            pass  # No-op: never log the request line

    # Attach state to the handler class so we can access it via closure.
    CallbackHandler.received_callback = property(
        lambda self: _callback_state["received_callback"]
    )
    CallbackHandler.received_code = property(lambda self: _callback_state["code"])
    CallbackHandler.received_state = property(lambda self: _callback_state["state"])
    CallbackHandler.received_error = property(lambda self: _callback_state["error"])

    return CallbackHandler
