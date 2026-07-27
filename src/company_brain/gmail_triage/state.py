"""Per-account cached triage state: last historyId, refresh time, bucketed messages."""

import json
from dataclasses import dataclass, asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from company_brain.gmail_triage.classify import EmailBucket


@dataclass
class Message:
    """A cached message for display in the triage dashboard."""

    id: str
    thread_id: str
    subject: str
    from_: str
    snippet: str
    received_at: str
    bucket: EmailBucket
    labels: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "threadId": self.thread_id,
            "subject": self.subject,
            "from": self.from_,
            "snippet": self.snippet,
            "receivedAt": self.received_at,
            "bucket": self.bucket,
            "labels": self.labels,
        }


@dataclass
class TriageState:
    """Cached inbox state for one account."""

    account_key: str
    last_history_id: str | None
    last_refreshed_at: str
    messages: dict[EmailBucket, list[Message]]

    @classmethod
    def default(cls, account_key: str) -> "TriageState":
        return cls(
            account_key=account_key,
            last_history_id=None,
            last_refreshed_at=datetime.now(UTC).isoformat(),
            messages={bucket: [] for bucket in EmailBucket},
        )

    def is_stale(self, max_age_minutes: int = 15) -> bool:
        """Check if cached state is older than max_age_minutes."""
        refreshed = datetime.fromisoformat(self.last_refreshed_at)
        age = datetime.now(UTC) - refreshed
        return age > timedelta(minutes=max_age_minutes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "accountKey": self.account_key,
            "lastHistoryId": self.last_history_id,
            "lastRefreshedAt": self.last_refreshed_at,
            "messages": {
                bucket: [msg.to_dict() for msg in messages]
                for bucket, messages in self.messages.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TriageState":
        messages = {}
        for bucket_str, msg_list in data.get("messages", {}).items():
            bucket = EmailBucket(bucket_str)
            messages[bucket] = [
                Message(
                    id=msg["id"],
                    thread_id=msg["threadId"],
                    subject=msg["subject"],
                    from_=msg["from"],
                    snippet=msg["snippet"],
                    received_at=msg["receivedAt"],
                    bucket=EmailBucket(msg["bucket"]),
                    labels=msg.get("labels", []),
                )
                for msg in msg_list
            ]
        return cls(
            account_key=data["accountKey"],
            last_history_id=data.get("lastHistoryId"),
            last_refreshed_at=data.get("lastRefreshedAt", datetime.now(UTC).isoformat()),
            messages=messages,
        )


class StateStore:
    """Persist per-account triage state to disk next to token store."""

    _CACHE_DIR = (
        Path("~/.config").expanduser()
        / "company_brain"
        / "triage"
    )

    @classmethod
    def path_for(cls, account_key: str) -> Path:
        """Path to the state file for this account."""
        return cls._CACHE_DIR / f"{account_key}.json"

    @classmethod
    def load(cls, account_key: str) -> TriageState | None:
        """Load cached state, or None if not stored."""
        path = cls.path_for(account_key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            return TriageState.from_dict(data)
        except (OSError, json.JSONDecodeError, ValueError):
            return None

    @classmethod
    def save(cls, state: TriageState) -> None:
        """Persist state atomically."""
        path = cls.path_for(state.account_key)
        path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)

        temp_path = path.parent / f".{state.account_key}.tmp"
        temp_path.write_text(json.dumps(state.to_dict(), indent=2))
        temp_path.chmod(0o600)
        temp_path.replace(path)
        path.parent.chmod(0o700)

    @classmethod
    def delete(cls, account_key: str) -> None:
        """Delete cached state, if it exists."""
        path = cls.path_for(account_key)
        path.unlink(missing_ok=True)
