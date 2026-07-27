"""Claude-backed extraction.

Resolves the open question in ARCHITECTURE §4.1. The two candidate mechanisms
for evidence spans were believed to be mutually exclusive; measured against the
live API they are not, given the right shape:

    output_config.format + citations  ->  400, "Citations cannot be enabled
                                          when output format is set"
    forced tool_choice + citations    ->  accepted, but the response is a lone
                                          tool_use block: no cited text is
                                          emitted, so no spans come back
    tool_choice auto + citations      ->  BOTH. Cited text blocks carrying
                                          API-computed start/end char offsets,
                                          followed by a schema-validated
                                          tool_use block.

So the extractor asks for prose *and* a tool call. The prose is where citations
attach; the tool call is where structure lives. Spans are computed by the API
against the document we sent, not reported by the model, which is the whole
point — §11's gates are only as good as the evidence a reviewer can check, and
a model-reported offset that lands on the wrong sentence is worse than none.
"""

from __future__ import annotations

import os
from typing import Any

import anthropic

from company_brain.extract.base import ExtractionRequest, ExtractionResult
from company_brain.extract.rules import Roster
from company_brain.schemas.edges import (
    Edge,
    Evidence,
    Predicate,
    Provenance,
    decide_status,
)

PROMPT_VERSION = "claude-roster-v1"
DEFAULT_MODEL = "claude-sonnet-5"

# Closed vocabulary. The model selects from the curated roster rather than
# naming entities itself — open-vocabulary extraction produces hundreds of
# near-duplicate nodes (§10.3), and no amount of downstream matching recovers
# from a name the model invented once and never repeated.
_EXTRACTABLE = (
    Predicate.MENTIONS,
    Predicate.OWNS,
    Predicate.HANDOFF_TO,
    Predicate.DEPENDS_ON,
    Predicate.SUPERSEDES,
)

SYSTEM = """\
You extract typed relations from one company document into a knowledge graph.

Rules:
- Only use entity ids from the roster you are given. Never invent an id. If
  something is referred to but is not on the roster, leave it out.
- Quote the document verbatim for every relation. The quote must appear in the
  document exactly as written.
- Distinguish what the document *asserts* from what it merely mentions. "Sam
  was quoted about the renewal" is a mention. "Sam owns renewals" is ownership.
  Prefer mentions when unsure; a wrong ownership edge is expensive to undo.
- Report nothing rather than guessing. Recall is not the goal here; a reviewer
  has to be able to check every edge you emit.

First state, in prose, what the document establishes about ownership, handoffs
and dependencies, quoting the source exactly. Then call record_relations."""


def _tool_schema(roster: Roster) -> dict[str, Any]:
    ids = sorted({entry.node_id for entry in roster.all()})
    return {
        "name": "record_relations",
        "description": "Record the typed relations found in this document.",
        # strict:true guarantees the input validates against the schema, so
        # there is no defensive parsing below.
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "relations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "predicate": {
                                "type": "string",
                                "enum": [str(p) for p in _EXTRACTABLE],
                            },
                            "object": {"type": "string", "enum": ids},
                            "quote": {"type": "string"},
                            "confidence": {"type": "number"},
                        },
                        "required": ["predicate", "object", "quote", "confidence"],
                        "additionalProperties": False,
                    },
                },
                "unresolved": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Surface strings that clearly name a person, team or tool "
                        "but match no roster id. Left unresolved on purpose."
                    ),
                },
            },
            "required": ["relations", "unresolved"],
            "additionalProperties": False,
        },
    }


class ClaudeExtractor:
    """Extraction via Claude, with API-computed evidence spans."""

    prompt_version = PROMPT_VERSION

    def __init__(
        self,
        roster: Roster,
        *,
        model: str = DEFAULT_MODEL,
        client: anthropic.Anthropic | None = None,
        max_tokens: int = 4096,
    ) -> None:
        self.roster = roster
        self._model = model
        self.max_tokens = max_tokens
        self.client = client or anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self._tool = _tool_schema(roster)
        self._roster_text = "\n".join(
            f"{entry.node_id}  ({', '.join(entry.surfaces)})"
            for entry in sorted(roster.all(), key=lambda e: e.node_id)
        )

    @property
    def model(self) -> str:
        return self._model

    def extract(self, request: ExtractionRequest) -> ExtractionResult:
        response = self.client.messages.create(
            model=self._model,
            max_tokens=self.max_tokens,
            system=SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "text",
                                "media_type": "text/plain",
                                "data": request.body,
                            },
                            "title": request.title,
                            # Enabling citations is what makes the API return
                            # real character offsets instead of the model's
                            # guess at them.
                            "citations": {"enabled": True},
                        },
                        {
                            "type": "text",
                            "text": f"Roster:\n{self._roster_text}\n\nExtract relations.",
                        },
                    ],
                }
            ],
            tools=[self._tool],  # type: ignore[list-item]
        )

        spans = _collect_spans(response.content)
        edges: list[Edge] = []
        unresolved: tuple[str, ...] = ()

        for block in response.content:
            if block.type != "tool_use" or block.name != "record_relations":
                continue
            payload: dict[str, Any] = dict(block.input)  # type: ignore[arg-type]
            unresolved = tuple(sorted(set(payload.get("unresolved", []))))
            for item in payload.get("relations", []):
                edge = self._to_edge(item, spans, request.body)
                if edge is not None:
                    edges.append(edge)

        deduped: dict[tuple[str, str], Edge] = {}
        for edge in edges:
            deduped.setdefault((str(edge.predicate), edge.object), edge)

        return ExtractionResult(
            edges=tuple(sorted(deduped.values(), key=lambda e: e.sort_key())),
            model=self._model,
            prompt_version=self.prompt_version,
            unresolved=unresolved,
        )

    def _to_edge(
        self, item: dict[str, Any], spans: list[tuple[str, int, int]], body: str
    ) -> Edge | None:
        quote = str(item["quote"]).strip()
        span = _match_span(quote, spans, body)
        if span is None:
            # No resolvable span means no checkable evidence. Dropping the edge
            # is correct: an Edge with llm provenance and no evidence is
            # rejected at construction anyway, and a §11 gate that cannot be
            # audited is not a gate.
            return None

        predicate = Predicate(item["predicate"])
        confidence = max(0.0, min(1.0, float(item["confidence"])))
        evidence = (Evidence(node="self", span=span, quote=body[span[0] : span[1]].strip()),)
        return Edge(
            predicate=predicate,
            object=item["object"],
            confidence=confidence,
            provenance=Provenance.LLM,
            status=decide_status(predicate, confidence, Provenance.LLM, evidence),
            evidence=evidence,
        )


def _collect_spans(content: list[Any]) -> list[tuple[str, int, int]]:
    """Pull (cited_text, start, end) out of the response's citation blocks."""
    out: list[tuple[str, int, int]] = []
    for block in content:
        if block.type != "text":
            continue
        for citation in getattr(block, "citations", None) or []:
            start = getattr(citation, "start_char_index", None)
            end = getattr(citation, "end_char_index", None)
            if start is None or end is None:
                continue  # page/block citations don't apply to plain text
            out.append((str(citation.cited_text), int(start), int(end)))
    return out


def _match_span(
    quote: str, spans: list[tuple[str, int, int]], body: str
) -> tuple[int, int] | None:
    """Resolve a model-supplied quote to a real offset range.

    Prefers an API-computed citation span that contains the quote. Falls back to
    an exact string search of the body — which is still a *verified* offset, just
    one we computed rather than the API. Never trusts an offset the model stated.
    """
    for cited, start, _end in spans:
        if quote and quote in cited:
            offset = cited.find(quote)
            return (start + offset, start + offset + len(quote))
    if quote:
        found = body.find(quote)
        if found != -1:
            return (found, found + len(quote))
    return None
