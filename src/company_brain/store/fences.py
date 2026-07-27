"""Generated regions inside a human-editable file.

Entity pages are synthesized, but a human must be able to annotate one and not
lose the annotation on the next ingest. So machine-owned content is fenced:

    <!-- cb:generated start region=mentions hash=9f21ab -->
    Mentioned in 34 documents.
    <!-- cb:generated end region=mentions -->

The rules (invariant 13):

* Text **outside** every fence is human-owned and never touched by a writer.
* A writer replaces a region's interior only if the interior still hashes to the
  recorded ``hash``. A mismatch means a human edited inside the fence, and the
  write is diverted to a proposal instead of clobbering them.

The hash is what makes this work: without it, "did a human touch this?" is
unanswerable and the safe default would be to never regenerate anything.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Final

HASH_LEN: Final = 8
_REGION_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

_START = re.compile(
    r"^[ \t]*<!--[ \t]*cb:generated[ \t]+start[ \t]+region=(?P<region>\S+)"
    r"[ \t]+hash=(?P<hash>[0-9a-f]+)[ \t]*-->[ \t]*$",
    re.MULTILINE,
)
_END = re.compile(
    r"^[ \t]*<!--[ \t]*cb:generated[ \t]+end[ \t]+region=(?P<region>\S+)[ \t]*-->[ \t]*$",
    re.MULTILINE,
)


class FenceError(ValueError):
    """The fence structure in a body is malformed."""


class RegionTampered(FenceError):
    """A human edited inside a generated region.

    Raised so the caller diverts to ``store/_proposals/`` rather than
    overwriting the edit. Carries both hashes for the review UI to show a diff.
    """

    def __init__(self, region: str, expected: str, actual: str) -> None:
        super().__init__(
            f"region {region!r} was edited by hand (recorded hash {expected}, found {actual})"
        )
        self.region = region
        self.expected = expected
        self.actual = actual


def region_hash(content: str) -> str:
    """Hash a region's interior. Normalizes the trailing newline so that a
    formatter adding or removing one doesn't read as human tampering."""
    normalized = content.strip("\n")
    return hashlib.blake2b(normalized.encode("utf-8"), digest_size=16).hexdigest()[:HASH_LEN]


@dataclass(frozen=True, slots=True)
class Region:
    """One fenced block found in a body."""

    name: str
    content: str
    recorded_hash: str
    start: int  # index of the opening marker line
    end: int  # index just past the closing marker line

    @property
    def is_intact(self) -> bool:
        return region_hash(self.content) == self.recorded_hash


def render_fence(name: str, content: str) -> str:
    """Render a complete fenced block, hash included."""
    if not _REGION_NAME.match(name):
        raise FenceError(f"invalid region name {name!r}: expected [a-z0-9][a-z0-9_-]*")
    inner = content.strip("\n")
    digest = region_hash(inner)
    body = f"\n{inner}\n" if inner else "\n"
    return (
        f"<!-- cb:generated start region={name} hash={digest} -->"
        f"{body}"
        f"<!-- cb:generated end region={name} -->"
    )


def find_regions(body: str) -> list[Region]:
    """Parse every fenced region in a body, in document order.

    Rejects nesting, crossed fences, and duplicate names — all of which would
    make "which bytes does this region own?" ambiguous, and an ambiguous answer
    here means a writer might destroy human text.
    """
    starts = list(_START.finditer(body))
    ends = list(_END.finditer(body))
    if len(starts) != len(ends):
        raise FenceError(
            f"unbalanced fences: {len(starts)} start marker(s), {len(ends)} end marker(s)"
        )

    regions: list[Region] = []
    seen: set[str] = set()
    cursor = 0

    for start_match, end_match in zip(starts, ends, strict=True):
        name = start_match.group("region")
        if start_match.start() < cursor:
            raise FenceError(f"region {name!r} overlaps or nests inside a previous region")
        if end_match.group("region") != name:
            raise FenceError(
                f"fence mismatch: region {name!r} is closed by {end_match.group('region')!r}"
            )
        if end_match.start() < start_match.end():
            raise FenceError(f"region {name!r} closes before it opens")
        if name in seen:
            raise FenceError(f"duplicate region {name!r}")
        seen.add(name)

        inner = body[start_match.end() : end_match.start()]
        regions.append(
            Region(
                name=name,
                content=inner.strip("\n"),
                recorded_hash=start_match.group("hash"),
                start=start_match.start(),
                end=end_match.end(),
            )
        )
        cursor = end_match.end()

    return regions


def get_region(body: str, name: str) -> Region | None:
    return next((r for r in find_regions(body) if r.name == name), None)


def upsert_region(body: str, name: str, content: str, *, force: bool = False) -> str:
    """Replace a region's interior, or append the region if it's absent.

    Raises ``RegionTampered`` when the existing interior no longer matches its
    recorded hash. ``force`` overrides that and is for the review-queue accept
    path only — a human has seen the diff by then and chosen to overwrite. No
    ingest path may pass it.
    """
    existing = get_region(body, name)
    fence = render_fence(name, content)

    if existing is None:
        prefix = body.rstrip("\n")
        return f"{prefix}\n\n{fence}\n" if prefix else f"{fence}\n"

    if not existing.is_intact and not force:
        raise RegionTampered(name, existing.recorded_hash, region_hash(existing.content))

    return body[: existing.start] + fence + body[existing.end :]


def strip_regions(body: str) -> str:
    """Return only the human-authored text, fences removed.

    Used by the indexer: generated regions are derived from edges that are
    already indexed, so chunking them would double-count the same content in
    retrieval and let a summary outrank its own source.
    """
    out: list[str] = []
    cursor = 0
    for region in find_regions(body):
        out.append(body[cursor : region.start])
        cursor = region.end
    out.append(body[cursor:])
    return re.sub(r"\n{3,}", "\n\n", "".join(out)).strip("\n")


def human_content_hash(body: str) -> str:
    """Hash only the human-authored text.

    Lets an ingest run tell "the machine's own regeneration changed this file"
    from "a person changed this file" without diffing the whole tree.
    """
    return hashlib.blake2b(strip_regions(body).encode("utf-8"), digest_size=16).hexdigest()[
        :HASH_LEN
    ]
