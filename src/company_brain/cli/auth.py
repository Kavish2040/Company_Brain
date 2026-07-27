"""OAuth authorization for connectors (Drive, etc.)."""

from __future__ import annotations

from typing import Annotated

import typer

auth_app = typer.Typer(help="OAuth setup for connectors that need it.")


@auth_app.command("drive")
def auth_drive(
    revoke: Annotated[
        bool,
        typer.Option(
            help="Delete the stored refresh token locally (does not revoke server-side)."
        ),
    ] = False,
) -> None:
    """Authorize company_brain to read your Google Drive (read-only).

    Opens your browser to Google's OAuth consent screen. Once approved, stores
    a refresh token locally at ~/.config/company_brain/tokens/gdrive.json
    (mode 0600). The token is used by `cb sync --connector gdrive`.

    Use --revoke to delete the local token (you can re-run this command anytime
    to re-authorize). Note: --revoke does NOT revoke the grant in your Google
    Account — to do that, visit https://myaccount.google.com/connections.
    """
    import os

    from company_brain.connectors.google_auth import (
        OAuthError,
        TokenStore,
        run_local_oauth_flow,
    )

    if revoke:
        TokenStore.delete("gdrive")
        typer.echo("gdrive token revoked locally.")
        typer.echo("  (To revoke server-side, visit https://myaccount.google.com/connections)")
        return

    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        typer.echo("GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set in environment.")
        typer.echo("  See .env.example for instructions.")
        raise typer.Exit(64)

    try:
        run_local_oauth_flow(
            client_id,
            client_secret,
            scope="https://www.googleapis.com/auth/drive.readonly",
            provider="gdrive",
        )
    except OAuthError as exc:
        typer.echo(f"Authorization failed: {exc}")
        raise typer.Exit(1) from exc

    typer.echo("Authorization complete!")
    typer.echo("  Refresh token stored at ~/.config/company_brain/tokens/gdrive.json")
    typer.echo("  You can now use: cb sync --connector gdrive --folder <folder-id>")
