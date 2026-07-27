"""Canonical markdown emit and parse.

This module is the whole of invariant 3 in practice. Everything it writes must
be a pure function of the model it was handed: same input, byte-identical
output, forever. The rules it enforces:

* a **declared** key order, not alphabetical — equally deterministic (the order
  is fixed in code) and far more readable in an editor, which is the point of
  keeping markdown canonical at all
* block-style YAML, LF endings, no trailing whitespace, exactly one final newline
* every collection sorted by a declared key before emit
* timestamps normalized to UTC and formatted identically for identical instants

Nothing here may consult the clock, the locale, the environment, or a hash seed.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Final

import yaml

from company_brain.schemas.acl import AclRef
from company_brain.schemas.edges import Edge, Evidence
from company_brain.schemas.nodes import Frontmatter, Node

FENCE: Final = "---"
_TRAILING_WS = re.compile(r"[ \t]+$", re.MULTILINE)

# Declared emit order. Identity first, then provenance, then relations last
# because it is the longest block and readers care about it least when skimming.
_KEY_ORDER: Final[tuple[str, ...]] = (
    "id",
    "type",
    "title",
    "status",
    "acl",
    "source",
    "authors",
    "aliases",
    "timestamps",
    "normalizer",
    "extraction",
    "redirects_to",
    "deleted_upstream_at",
    "content_retained",
    "relations",
)


class CanonicalDumper(yaml.SafeDumper):
    """SafeDumper with indentation that survives round-tripping."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        # Without this, pyyaml writes sequence items flush with their parent key,
        # which is legal YAML but reparses inconsistently across editors.
        super().increase_indent(flow=flow, indentless=False)


def _format_dt(value: datetime) -> str:
    """RFC-3339 in UTC. Microseconds appear only when non-zero — still a pure
    function of the instant, so determinism holds."""
    aware = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    utc = aware.astimezone(UTC)
    if utc.microsecond:
        return utc.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
    return utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


CanonicalDumper.add_representer(
    str, lambda d, v: d.represent_scalar("tag:yaml.org,2002:str", v)
)
CanonicalDumper.add_representer(
    datetime, lambda d, v: d.represent_scalar("tag:yaml.org,2002:str", _format_dt(v))
)
# Nested models keep their StrEnum members as enum instances under
# model_dump(mode="python"), and pyyaml's str representer is exact-type. One
# multi-representer covers every enum in the schema package, including ones
# added later.
CanonicalDumper.add_multi_representer(
    StrEnum, lambda d, v: d.represent_scalar("tag:yaml.org,2002:str", str(v))
)


class _Inline(list[Any]):
    """A list that emits flow-style. Spans as `[412, 431]` rather than a
    four-line block — the file is meant to be skimmed."""


CanonicalDumper.add_representer(
    _Inline, lambda d, v: d.represent_sequence("tag:yaml.org,2002:seq", v, flow_style=True)
)


def _prune(value: Any) -> Any:
    """Drop None and empty collections so absent fields don't clutter the file."""
    if isinstance(value, Mapping):
        cleaned = {k: _prune(v) for k, v in value.items()}
        return {k: v for k, v in cleaned.items() if v is not None and v != {} and v != []}
    if isinstance(value, _Inline):
        return value  # already scalars; rebuilding would drop the flow-style marker
    if isinstance(value, (list, tuple)):
        return [_prune(v) for v in value]
    return value


def _evidence_to_dict(ev: Evidence) -> dict[str, Any]:
    out: dict[str, Any] = {"node": ev.node}
    if ev.span is not None:
        out["span"] = _Inline([ev.span[0], ev.span[1]])
    if ev.quote is not None:
        out["quote"] = ev.quote
    return out


def _edge_to_dict(edge: Edge) -> dict[str, Any]:
    out: dict[str, Any] = {"predicate": str(edge.predicate)}
    if edge.subject is not None:
        out["subject"] = edge.subject
    out |= {
        "object": edge.object,
        "confidence": round(edge.confidence, 4),
        "provenance": str(edge.provenance),
        "status": str(edge.status),
    }
    if edge.evidence:
        out["evidence"] = [_evidence_to_dict(e) for e in edge.evidence]
    return out


def sort_edges(edges: Iterable[Edge]) -> list[Edge]:
    return sorted(edges, key=lambda e: e.sort_key())


def _acl_to_dict(acl: AclRef) -> dict[str, Any]:
    return {"ref": acl.ref, "sensitivity": str(acl.sensitivity)}


def frontmatter_to_mapping(fm: Frontmatter) -> dict[str, Any]:
    """Frontmatter -> plain dict in canonical order. Exposed for the indexer,
    which needs the same view without paying for a YAML round trip."""
    raw = fm.model_dump(mode="python")
    raw["type"] = str(fm.type)
    raw["status"] = str(fm.status)
    raw["acl"] = _acl_to_dict(fm.acl)
    raw["authors"] = sorted(fm.authors)
    raw["aliases"] = sorted(fm.aliases)
    raw["relations"] = [_edge_to_dict(e) for e in sort_edges(fm.relations)]

    ordered = {key: raw[key] for key in _KEY_ORDER if key in raw}
    leftover = sorted(set(raw) - set(_KEY_ORDER))
    if leftover:
        # A new field was added to Frontmatter without being placed in
        # _KEY_ORDER. Emitting it in sorted position keeps output deterministic;
        # the test suite fails so someone assigns it a real position.
        ordered.update({k: raw[k] for k in leftover})
    pruned: dict[str, Any] = _prune(ordered)
    return pruned


def dump_frontmatter(fm: Frontmatter) -> str:
    text: str = yaml.dump(
        frontmatter_to_mapping(fm),
        Dumper=CanonicalDumper,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=4096,
        indent=2,
    )
    return text


def normalize_body(body: str) -> str:
    """CRLF -> LF, strip trailing whitespace, collapse the tail to one newline."""
    text = body.replace("\r\n", "\n").replace("\r", "\n")
    text = _TRAILING_WS.sub("", text)
    return text.strip("\n")


def dump_node(node: Node) -> str:
    """Render a node to its canonical bytes."""
    body = normalize_body(node.body)
    parts = [FENCE, "\n", dump_frontmatter(node.frontmatter), FENCE, "\n"]
    if body:
        parts.extend(["\n", body, "\n"])
    return "".join(parts)


class MalformedNodeError(ValueError):
    """The file on disk is not a canonical node."""


def split_document(text: str) -> tuple[str, str]:
    """Split raw file text into (frontmatter yaml, body). Tolerant of CRLF and a
    leading BOM so a file edited on Windows still parses."""
    cleaned = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    if not cleaned.startswith(FENCE + "\n"):
        raise MalformedNodeError("file does not begin with a '---' frontmatter fence")
    rest = cleaned[len(FENCE) + 1 :]
    end = rest.find("\n" + FENCE)
    if end == -1:
        raise MalformedNodeError("unterminated frontmatter block")
    yaml_text = rest[:end]
    after = rest[end + len(FENCE) + 1 :]
    return yaml_text, after.lstrip("\n")


def parse_node(text: str) -> Node:
    """Parse canonical bytes back into a Node.

    Round-trip contract, asserted in tests: ``dump_node(parse_node(s)) == s`` for
    any ``s`` this module produced.
    """
    yaml_text, body = split_document(text)
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise MalformedNodeError(f"frontmatter is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise MalformedNodeError("frontmatter must be a mapping")
    return Node(frontmatter=Frontmatter.model_validate(data), body=normalize_body(body))
