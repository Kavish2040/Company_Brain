"""Node identity.

An ID is ``<type_plural>/<slug>`` and is identical to the file's path under the
store root, minus the ``.md`` suffix. IDs are immutable (invariant 12): a rename
writes a new node and leaves a ``redirects_to`` tombstone at the old ID, so a
citation issued last quarter still resolves.

Document slugs get a ``-<hash6>`` suffix derived from the canonical source URI.
The readable half is for humans; the hash half keeps the ID stable when a
document is retitled and prevents two ``meeting-notes.md`` from colliding.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Final

SLUG_HASH_LEN: Final = 6

_SEPARATORS = re.compile(r"[\s_/\\]+")
_DISALLOWED = re.compile(r"[^a-z0-9-]+")
_RUNS = re.compile(r"-{2,}")

# Kept in sync with NodeType in schemas/nodes.py; a test asserts the two agree.
TYPE_PLURALS: Final[dict[str, str]] = {
    "Document": "documents",
    "Person": "people",
    "Account": "accounts",
    "Team": "teams",
    "Tool": "tools",
    "Process": "processes",
    "Decision": "decisions",
}


def slugify(text: str, *, max_len: int = 60) -> str:
    """Lowercase ASCII slug. Pure and locale-independent (invariant 3).

    NFKD-folds accents rather than dropping them, so ``Zoë`` and ``Zoe`` produce
    the same slug instead of ``zo`` and ``zoe``.
    """
    folded = unicodedata.normalize("NFKD", text)
    ascii_only = folded.encode("ascii", "ignore").decode("ascii")
    s = _SEPARATORS.sub("-", ascii_only.lower())
    s = _DISALLOWED.sub("-", s)
    s = _RUNS.sub("-", s).strip("-")
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s or "untitled"


def uri_hash(source_uri: str, length: int = SLUG_HASH_LEN) -> str:
    """Stable short hash of a canonical source URI.

    blake2b rather than sha256 only because it takes a digest_size directly.
    """
    return hashlib.blake2b(source_uri.encode("utf-8"), digest_size=16).hexdigest()[:length]


def document_slug(title: str, source_uri: str) -> str:
    return f"{slugify(title)}-{uri_hash(source_uri)}"


def make_id(node_type: str, slug: str) -> str:
    try:
        plural = TYPE_PLURALS[node_type]
    except KeyError:
        raise ValueError(f"unknown node type: {node_type!r}") from None
    return f"{plural}/{slug}"


def split_id(node_id: str) -> tuple[str, str]:
    """Return ``(node_type, slug)``. Raises on anything that isn't a valid ID."""
    plural, sep, slug = node_id.partition("/")
    if not sep or not slug:
        raise ValueError(f"malformed node id: {node_id!r}")
    for node_type, candidate in TYPE_PLURALS.items():
        if candidate == plural:
            return node_type, slug
    raise ValueError(f"unknown type segment in node id: {node_id!r}")


def id_to_path(node_id: str) -> str:
    """Store-relative path for a node ID. Validates the ID on the way through."""
    split_id(node_id)
    return f"{node_id}.md"
