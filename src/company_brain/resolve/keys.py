"""Normalization, blocking keys, and identity keys.

Pure functions over strings. Nothing here reads the store, the clock, or the
environment, and nothing iterates a set in a way that reaches an output — layer
3's whole output ordering is downstream of these, so a `hash()`-dependent
ordering here would surface as a store that differs between processes.

Two ideas that are easy to conflate and are kept apart deliberately:

* A **blocking key** is a cheap, deliberately lossy bucket. Sharing one means
  "worth comparing", nothing more. Its job is recall, and a key that never
  collides is a key that never generates a candidate.
* An **identity key** is a claim from a source system — a corporate email, a
  directory ID. Sharing one is layer 1 evidence appearing inside layer 3's
  score; *disagreeing* on one is the strongest negative signal available here,
  and is what stops the §10.2 "two real people, one short name" failure.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Final

# Domains where "same domain, different local part" says nothing about identity.
# At a corporate directory it says a great deal — two distinct accounts — which
# is what `identity_conflict` turns into a veto. At a consumer mail provider the
# same shape is just two of anyone's addresses, so those domains are excluded.
# Deliberately short and hand-written: the failure mode of an over-long list is
# silently disarming the veto for a domain that is somebody's real directory.
PERSONAL_EMAIL_DOMAINS: Final[frozenset[str]] = frozenset(
    {
        "aol.com",
        "gmail.com",
        "googlemail.com",
        "hotmail.com",
        "icloud.com",
        "live.com",
        "me.com",
        "outlook.com",
        "proton.me",
        "protonmail.com",
        "yahoo.com",
    }
)

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_NON_WORD = re.compile(r"[^a-z0-9@.+_-]+")
_RUNS = re.compile(r"\s{2,}")
_TOKEN = re.compile(r"[a-z0-9]+")

# Honorifics and suffixes carry no identity signal and wreck a "last token is
# the surname" rule. "Priya Raman Jr." must still key on `raman`.
_NAME_NOISE: Final[frozenset[str]] = frozenset(
    {"dr", "i", "ii", "iii", "iv", "jr", "md", "mr", "mrs", "ms", "mx", "phd", "prof", "sr"}
)


def fold(text: str) -> str:
    """Lowercase, NFKD-fold accents, collapse whitespace.

    Same folding rule as `schemas.ids.slugify` — ``Zoë`` and ``Zoe`` must land
    in the same block or the accented spelling can never be resolved against
    the unaccented one.
    """
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    return _RUNS.sub(" ", _NON_WORD.sub(" ", ascii_only.lower())).strip()


def is_email(surface: str) -> bool:
    return bool(_EMAIL.match(surface.strip()))


@dataclass(frozen=True, slots=True, order=True)
class Email:
    """A parsed address. ``local`` is dot- and tag-stripped so that
    ``sam.kaur+drive@`` and ``samkaur@`` compare equal at the same domain."""

    local: str
    domain: str

    @property
    def address(self) -> str:
        return f"{self.local}@{self.domain}"

    @property
    def is_personal(self) -> bool:
        return self.domain in PERSONAL_EMAIL_DOMAINS


def parse_email(surface: str) -> Email | None:
    if not is_email(surface):
        return None
    raw_local, _, domain = surface.strip().lower().partition("@")
    local = raw_local.partition("+")[0].replace(".", "")
    if not local or not domain:
        return None
    return Email(local=local, domain=domain)


def emails_of(surfaces: tuple[str, ...]) -> tuple[Email, ...]:
    """Every address in a set of surface forms, deduplicated and sorted."""
    parsed = {e.address: e for s in surfaces if (e := parse_email(s)) is not None}
    return tuple(parsed[key] for key in sorted(parsed))


def name_tokens(surface: str) -> tuple[str, ...]:
    """Identity-bearing tokens of a name, in order, noise words dropped."""
    return tuple(t for t in _TOKEN.findall(fold(surface)) if t not in _NAME_NOISE)


def surname_key(surface: str) -> str | None:
    """The blocking key for a family name: the last token, if it is one.

    A single-character last token is an initial, not a surname — "Sam K."
    blocks on nothing here, which is the correct outcome: §10.2 wants that
    string left ambiguous rather than bucketed with one of the two people it
    could mean.
    """
    tokens = name_tokens(surface)
    if not tokens:
        return None
    last = tokens[-1]
    return last if len(last) > 1 else None


def initials_key(surface: str) -> str | None:
    """First initial plus surname: ``Samantha Kaur`` and ``S. Kaur`` -> ``skaur``.

    The point of this key is exactly the abbreviation case, so it needs two or
    more tokens; a bare surname would key identically to itself and add nothing
    the surname key does not already cover.
    """
    tokens = name_tokens(surface)
    if len(tokens) < 2:
        return None
    last = tokens[-1]
    return f"{tokens[0][0]}{last}" if len(last) > 1 else None


def trigrams(surface: str) -> tuple[str, ...]:
    """Padded character trigrams of a name, sorted and deduplicated.

    Built from `name_tokens` rather than the raw fold so that punctuation and
    honorifics cannot move the score: ``S. Kaur`` and ``S Kaur`` are the same
    string by the time they get here.
    """
    padded = "  " + "_".join(name_tokens(surface)) + "  "
    return tuple(sorted({padded[i : i + 3] for i in range(len(padded) - 2)}))


def dice(left: str, right: str) -> float:
    """Sorensen-Dice over character trigrams, in [0, 1].

    Chosen over an edit distance because it is symmetric, needs no length
    normalization, and degrades sensibly on reordered name parts ("Kaur, Sam").
    It is also cheap enough to run on every candidate pair without a cache.
    """
    a, b = trigrams(left), trigrams(right)
    if not a or not b:
        return 0.0
    shared = len(set(a) & set(b))  # membership only; never an output order
    return round(2.0 * shared / (len(a) + len(b)), 6)


def jaccard(left: tuple[str, ...], right: tuple[str, ...]) -> float:
    """Overlap of two sorted, deduplicated tuples, in [0, 1]."""
    if not left or not right:
        return 0.0
    a, b = set(left), set(right)
    return round(len(a & b) / len(a | b), 6)


def identity_keys(surfaces: tuple[str, ...]) -> tuple[str, ...]:
    """Source-system identity claims found among an entity's surface forms.

    Only addresses today, because that is what the connectors in this repo
    actually carry. Slack and directory IDs belong here the moment layer 1
    writes them onto entity nodes; the shape (`kind:value`, sorted) is chosen so
    adding them is a new prefix and not a new code path.
    """
    return tuple(f"email:{e.address}" for e in emails_of(surfaces))


def identity_surface(surfaces: tuple[str, ...], key: str) -> str:
    """The address *as written* that produced an identity key.

    Matching normalizes (dots and ``+tags`` stripped), which is right for
    comparison and wrong for a reviewer: quoting ``samkaur@meridian.example``
    as evidence when the file says ``sam.kaur@meridian.example`` invites the
    reasonable objection that the evidence was fabricated. Sorted, so the
    choice among several equivalent spellings is stable.
    """
    for surface in sorted(surfaces):
        email = parse_email(surface)
        if email is not None and f"email:{email.address}" == key:
            return surface.strip().lower()
    return key.partition(":")[2]


def identity_conflict(left: tuple[str, ...], right: tuple[str, ...]) -> str | None:
    """A reason these two are *different* entities, or None.

    Two distinct accounts in the same corporate directory is the one negative
    signal strong enough to overrule everything positive. Sam Kaur and Sam Kelly
    score well on name, team, channel and co-occurrence — §10.2 notes that
    working together makes those features actively worse — and they hold
    ``sam.kaur@`` and ``sam.kelly@`` at the same domain, which settles it.
    """

    def corporate(side: tuple[str, ...]) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        for email in emails_of(side):
            if not email.is_personal:
                out.setdefault(email.domain, set()).add(email.local)
        return out

    mine, theirs = corporate(left), corporate(right)
    # Both sides must be present at the domain and share no local part. One
    # side holding two aliases at one domain is a person with two aliases, not
    # a conflict — computing this over the union instead makes every such
    # entity unmergeable with anything.
    for domain in sorted(set(mine) & set(theirs)):
        if not (mine[domain] & theirs[domain]):
            listed = ", ".join(sorted(mine[domain] | theirs[domain]))
            return f"distinct accounts at {domain} ({listed})"
    return None
