"""Source bytes -> markdown. Pure functions, no exceptions.

Every normalizer here is a pure function of ``(bytes, config)`` and its own
version string (invariant 3). No clock, no locale, no randomness, no network.
If a normalizer ever needs one of those, it belongs in a connector instead.

The version travels into the node's frontmatter so a converter upgrade shows up
as a reviewable corpus diff rather than silent churn.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, runtime_checkable

_WS_RUN = re.compile(r"[ \t]{2,}")
_BLANK_RUN = re.compile(r"\n{3,}")


@dataclass(frozen=True, slots=True)
class Normalized:
    """What a normalizer produces. Everything here is derived from the input."""

    body: str
    title: str
    created: datetime | None = None
    modified: datetime | None = None
    authors: tuple[str, ...] = ()
    # Surface strings the connector could not resolve to an ID (email addresses,
    # @handles). Entity resolution consumes these; see ARCHITECTURE §10.
    author_hints: tuple[str, ...] = ()
    extra: dict[str, str] = field(default_factory=dict)


@runtime_checkable
class Normalizer(Protocol):
    # Read-only properties, not bare annotations: implementations declare these
    # as class-level constants, which do not satisfy a mutable protocol member.
    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    @property
    def suffixes(self) -> tuple[str, ...]: ...

    def normalize(self, raw: bytes) -> Normalized: ...


class NormalizeError(ValueError):
    """The bytes could not be converted."""


def content_sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def tidy(text: str) -> str:
    """Collapse whitespace noise without touching structure.

    Deliberately conservative: it does not reflow paragraphs or normalize
    punctuation, because those would make the markdown diverge from the source
    in ways a reader comparing the two would find confusing.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    lines = [_WS_RUN.sub(" ", line).rstrip() for line in text.split("\n")]
    return _BLANK_RUN.sub("\n\n", "\n".join(lines)).strip("\n")


def decode(raw: bytes) -> str:
    """UTF-8 with a deterministic fallback.

    Falls back to cp1252 rather than latin-1 because real corporate documents
    carry smart quotes and em dashes, which latin-1 maps to control characters.
    """
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


class Registry:
    """Maps a file suffix to the normalizer that owns it."""

    def __init__(self) -> None:
        self._by_suffix: dict[str, Normalizer] = {}

    def register(self, normalizer: Normalizer) -> None:
        for suffix in normalizer.suffixes:
            if suffix in self._by_suffix:
                raise RuntimeError(
                    f"{suffix!r} is claimed by both "
                    f"{self._by_suffix[suffix].name} and {normalizer.name}"
                )
            self._by_suffix[suffix] = normalizer

    def for_suffix(self, suffix: str) -> Normalizer | None:
        return self._by_suffix.get(suffix.lower())

    def suffixes(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_suffix))
