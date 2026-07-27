"""Apollo lead lookup, over httpx.

Lead resolution only: given a person the graph already knows about, return
whatever contact record Apollo holds for them. There is no send path here, and
adding one is a decision rather than an extension — Apollo's sequence API mails
real people, and nothing in this package should be able to do that as a side
effect of a lookup.

The provider choice mirrors `app.choose_providers`: a key selects the live
client, its absence selects a deterministic offline one, and the reason is
carried on the object so a caller can report which it got. That is what keeps
the test suite free and the CI run reproducible — an outreach test that needs a
paid API key is a test that stops being run.

`reveal_personal_emails` is deliberately never set. It costs Apollo credits per
call and returns personal addresses for people who did not ask to be contacted
at them; the work address Apollo returns by default is the one appropriate to
company outreach.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

import httpx

APOLLO_BASE = "https://api.apollo.io/api/v1"
MATCH_PATH = "/people/match"
TIMEOUT_SECONDS = 15.0


class ApolloError(RuntimeError):
    """Apollo refused, rate-limited, or returned something unparseable."""


@dataclass(frozen=True, slots=True)
class Lead:
    """A person as a contactable lead, not as a graph node.

    ``source`` names which client produced it. It travels with the record all
    the way to the reviewer, because "Apollo says this is their address" and
    "we guessed this from a corpus fixture" are different claims and only one
    of them should be acted on.
    """

    name: str
    email: str | None
    title: str | None
    organization: str | None
    linkedin_url: str | None
    source: str

    @property
    def contactable(self) -> bool:
        return bool(self.email)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "email": self.email,
            "title": self.title,
            "organization": self.organization,
            "linkedin_url": self.linkedin_url,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Lead:
        return cls(
            name=str(raw.get("name", "")),
            email=raw.get("email"),
            title=raw.get("title"),
            organization=raw.get("organization"),
            linkedin_url=raw.get("linkedin_url"),
            source=str(raw.get("source", "offline")),
        )


@runtime_checkable
class LeadSource(Protocol):
    """What the draft path needs. One method, so the offline client is a peer
    of the live one rather than a mock of it."""

    @property
    def name(self) -> str: ...

    def find(self, full_name: str, *, organization: str | None = None) -> Lead | None: ...


class ApolloClient:
    """Live Apollo lead lookup.

    One `httpx.Client` per instance, reused across calls — Apollo rate-limits
    per key, and a fresh connection per lookup wastes the TLS handshake on
    every draft.
    """

    name = "apollo"

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = APOLLO_BASE,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise ApolloError("ApolloClient needs an API key; use OfflineLeadSource instead")
        self._key = api_key
        self._base = base_url.rstrip("/")
        self._client = client or httpx.Client(timeout=TIMEOUT_SECONDS)

    def find(self, full_name: str, *, organization: str | None = None) -> Lead | None:
        """Resolve one person to a lead. `None` means Apollo has no match.

        A miss is not an error: most people in an internal knowledge graph are
        not in Apollo's B2B database, and raising would turn the common case
        into a failed request.
        """
        first, _, last = full_name.strip().partition(" ")
        payload: dict[str, Any] = {"first_name": first, "last_name": last or first}
        if organization:
            payload["organization_name"] = organization

        try:
            response = self._client.post(
                f"{self._base}{MATCH_PATH}",
                json=payload,
                headers={
                    "x-api-key": self._key,
                    "Content-Type": "application/json",
                    "Cache-Control": "no-cache",
                },
            )
        except httpx.HTTPError as exc:
            raise ApolloError(f"apollo request failed: {type(exc).__name__}") from exc

        # 404 is "no such person", which is a miss. Everything else that is not
        # a 2xx is a real failure and must not be smoothed into one.
        if response.status_code == 404:
            return None
        if response.status_code == 429:
            raise ApolloError("apollo rate limit reached")
        if response.status_code >= 400:
            raise ApolloError(f"apollo returned {response.status_code}")

        try:
            person = response.json().get("person")
        except ValueError as exc:
            raise ApolloError("apollo returned a non-JSON body") from exc
        if not isinstance(person, dict):
            return None
        return _lead_from_person(person, fallback_name=full_name)


def _lead_from_person(person: dict[str, Any], *, fallback_name: str) -> Lead:
    org = person.get("organization")
    return Lead(
        name=str(person.get("name") or fallback_name),
        email=person.get("email"),
        title=person.get("title"),
        organization=(org.get("name") if isinstance(org, dict) else None),
        linkedin_url=person.get("linkedin_url"),
        source="apollo",
    )


class OfflineLeadSource:
    """No network, no key, same shape.

    Returns `None` rather than a fabricated address. A plausible-looking email
    that nobody verified is worse than no email at all here: the reviewer's
    whole job is deciding whether to contact this person, and a fake contact
    detail is the one input that makes that decision wrong while looking right.
    What it *does* carry is the name, so the draft still composes and the
    review flow is exercisable offline.
    """

    name = "offline"

    def find(self, full_name: str, *, organization: str | None = None) -> Lead | None:
        return Lead(
            name=full_name,
            email=None,
            title=None,
            organization=organization,
            linkedin_url=None,
            source="offline",
        )


@dataclass(frozen=True, slots=True)
class LeadProvider:
    """The chosen client plus why it was chosen, reported like `Providers`."""

    source: LeadSource
    live: bool
    reason: str


def choose_lead_source() -> LeadProvider:
    """Live Apollo when `APOLLO_API_KEY` is set and offline is not forced.

    `COMPANY_BRAIN_OFFLINE` wins over a present key, so the switch that makes
    the rest of the system free and deterministic does the same thing here.
    """
    if os.environ.get("COMPANY_BRAIN_OFFLINE", "").strip().lower() in {"1", "true", "yes"}:
        return LeadProvider(
            source=OfflineLeadSource(),
            live=False,
            reason="offline lead source (COMPANY_BRAIN_OFFLINE is set)",
        )

    key = os.environ.get("APOLLO_API_KEY", "").strip()
    if not key:
        return LeadProvider(
            source=OfflineLeadSource(),
            live=False,
            reason="offline lead source (APOLLO_API_KEY not set)",
        )
    return LeadProvider(source=ApolloClient(key), live=True, reason="live apollo lead lookup")
