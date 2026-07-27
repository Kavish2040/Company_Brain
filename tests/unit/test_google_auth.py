"""Tests for Google OAuth flow and credential management."""

from __future__ import annotations

import json
import os
import stat
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest import mock

import httpx
import pytest

from company_brain.connectors.google_auth import (
    GoogleOAuthCredentials,
    OAuthError,
    TokenStore,
    build_authorization_url,
    exchange_code_for_tokens,
)


class TestTokenStore:
    """Token persistence with correct file permissions."""

    def test_save_creates_file_with_mode_0600(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Saved token file has mode 0600."""
        config_dir = tmp_path / "config"
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        monkeypatch.setattr(TokenStore, "_CONFIG_DIR", config_dir / "company_brain" / "tokens")

        data = {"refresh_token": "test-token"}
        TokenStore.save("test-provider", data)

        path = TokenStore.path_for("test-provider")
        assert path.exists()
        mode = stat.filemode(path.stat().st_mode)
        assert mode.endswith("------"), f"expected mode 0600, got {mode}"

    def test_save_creates_parent_dir_with_mode_0700(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Parent directory has mode 0700."""
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        monkeypatch.setattr(TokenStore, "_CONFIG_DIR", tmp_path / "company_brain" / "tokens")

        TokenStore.save("test-provider", {"refresh_token": "token"})

        parent = TokenStore.path_for("test-provider").parent
        mode = stat.filemode(parent.stat().st_mode)
        assert mode.startswith("d"), "not a directory"
        # Owner rwx, group/other none: 0700.
        assert mode.endswith("------"), f"expected mode 0700, got {mode}"

    def test_load_existing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Load an existing token."""
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        monkeypatch.setattr(TokenStore, "_CONFIG_DIR", tmp_path / "company_brain" / "tokens")

        data = {"refresh_token": "stored-token"}
        TokenStore.save("provider-a", data)
        loaded = TokenStore.load("provider-a")
        assert loaded == data

    def test_load_missing_returns_none(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Load a non-existent token returns None."""
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        monkeypatch.setattr(TokenStore, "_CONFIG_DIR", tmp_path / "company_brain" / "tokens")

        result = TokenStore.load("nonexistent")
        assert result is None

    def test_delete(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Delete removes the token file."""
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        monkeypatch.setattr(TokenStore, "_CONFIG_DIR", tmp_path / "company_brain" / "tokens")

        TokenStore.save("provider-b", {"refresh_token": "token"})
        assert TokenStore.load("provider-b") is not None

        TokenStore.delete("provider-b")
        assert TokenStore.load("provider-b") is None

    def test_delete_missing_is_noop(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Delete a non-existent token doesn't error."""
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        monkeypatch.setattr(TokenStore, "_CONFIG_DIR", tmp_path / "company_brain" / "tokens")

        TokenStore.delete("nonexistent")  # Should not raise.


class TestGoogleOAuthCredentials:
    """OAuth credential loading and token refresh."""

    def test_load_reads_env_vars_and_stored_token(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Load reads environment variables and disk token."""
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "client-id-123")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "client-secret-456")
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        monkeypatch.setattr(TokenStore, "_CONFIG_DIR", tmp_path / "config" / "tokens")

        TokenStore.save("test", {"refresh_token": "refresh-token-xyz"})
        creds = GoogleOAuthCredentials.load("test")

        assert creds.client_id == "client-id-123"
        assert creds.client_secret == "client-secret-456"
        assert creds.refresh_token == "refresh-token-xyz"

    def test_load_missing_client_id_raises(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Load raises OAuthError if GOOGLE_CLIENT_ID is missing."""
        monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "secret")
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

        with pytest.raises(OAuthError, match="GOOGLE_CLIENT_ID"):
            GoogleOAuthCredentials.load("test")

    def test_load_missing_refresh_token_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Load raises OAuthError if no stored refresh token."""
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "client-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "secret")

        with pytest.raises(OAuthError, match="no stored refresh token"):
            GoogleOAuthCredentials.load("never-saved")

    def test_bearer_token_caches_until_expiry(self) -> None:
        """Bearer token is cached and refreshed after expiry (with margin)."""
        creds = GoogleOAuthCredentials(
            client_id="cid",
            client_secret="cs",
            refresh_token="rt",
        )

        # Mock the refresh endpoint.
        now = datetime.now(UTC)
        expires_in = 3600  # 1 hour

        def mock_post(*args: Any, **kwargs: Any) -> httpx.Response:
            """Mock httpx.post for token refresh."""
            return httpx.Response(
                200,
                json={
                    "access_token": "access-123",
                    "expires_in": expires_in,
                    "token_type": "Bearer",
                },
            )

        with mock.patch("company_brain.connectors.google_auth.httpx.post", side_effect=mock_post):
            # First call to bearer_token triggers refresh.
            token1 = creds.bearer_token()
            assert token1 == "access-123"
            expiry1 = creds._expiry

            # Second call returns cached token (still valid).
            token2 = creds.bearer_token()
            assert token2 == "access-123"
            assert creds._expiry == expiry1  # No refresh

            # Simulate expiry (minus the 60s margin).
            creds._expiry = datetime.now(UTC) + timedelta(seconds=50)  # Less than 60s remaining

            # Next call should refresh.
            def mock_post_2(*args: Any, **kwargs: Any) -> httpx.Response:
                return httpx.Response(
                    200,
                    json={
                        "access_token": "access-456",
                        "expires_in": expires_in,
                        "token_type": "Bearer",
                    },
                )

            with mock.patch("company_brain.connectors.google_auth.httpx.post", side_effect=mock_post_2):
                token3 = creds.bearer_token()
                assert token3 == "access-456"  # New token

    def test_bearer_token_refresh_failure_raises(self) -> None:
        """Refresh failure raises OAuthError with actionable message."""

        def mock_post_error(*args: Any, **kwargs: Any) -> httpx.Response:
            return httpx.Response(
                400,
                json={
                    "error": "invalid_grant",
                    "error_description": "Token has been revoked",
                },
            )

        creds = GoogleOAuthCredentials(
            client_id="cid",
            client_secret="cs",
            refresh_token="expired-rt",
        )

        with mock.patch("company_brain.connectors.google_auth.httpx.post", side_effect=mock_post_error):
            with pytest.raises(OAuthError, match="invalid_grant"):
                creds.bearer_token()


class TestAuthorizationUrl:
    """PKCE and CSRF parameter building."""

    def test_build_authorization_url_includes_required_params(self) -> None:
        """Authorization URL includes PKCE, state, offline access, consent."""
        url = build_authorization_url(
            client_id="client-123",
            redirect_uri="http://127.0.0.1:8080/callback",
            scope="https://www.googleapis.com/auth/drive.readonly",
            state="state-abc",
            code_challenge="challenge-xyz",
        )

        assert "response_type=code" in url
        assert "access_type=offline" in url
        assert "prompt=consent" in url
        assert "state=state-abc" in url
        assert "code_challenge_method=S256" in url
        assert "code_challenge=challenge-xyz" in url
        assert "client_id=client-123" in url


class TestCodeExchange:
    """Authorization code exchange for tokens."""

    def test_exchange_code_for_tokens_success(self) -> None:
        """Successful code exchange returns tokens."""

        def mock_post(*args: Any, **kwargs: Any) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "access_token": "access-abc",
                    "refresh_token": "refresh-xyz",
                    "expires_in": 3600,
                    "token_type": "Bearer",
                },
            )

        with mock.patch("company_brain.connectors.google_auth.httpx.post", side_effect=mock_post):
            tokens = exchange_code_for_tokens(
                client_id="cid",
                client_secret="cs",
                code="auth-code-123",
                redirect_uri="http://127.0.0.1:8080/callback",
                code_verifier="verifier-abc",
            )

        assert tokens["access_token"] == "access-abc"
        assert tokens["refresh_token"] == "refresh-xyz"

    def test_exchange_code_for_tokens_failure_raises(self) -> None:
        """Exchange failure raises OAuthError."""

        def mock_post(*args: Any, **kwargs: Any) -> httpx.Response:
            return httpx.Response(
                400,
                json={"error": "invalid_code", "error_description": "Code not valid"},
            )

        with mock.patch("company_brain.connectors.google_auth.httpx.post", side_effect=mock_post):
            with pytest.raises(OAuthError, match="code exchange failed"):
                exchange_code_for_tokens(
                    client_id="cid",
                    client_secret="cs",
                    code="bad-code",
                    redirect_uri="http://127.0.0.1:8080/callback",
                    code_verifier="verifier",
                )
