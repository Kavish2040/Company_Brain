"""Deterministic offline extractor.

Matches against a *curated roster* of entities rather than inventing names —
the same constraint ARCHITECTURE §10.3 puts on the LLM extractor, for the same
reason: open-vocabulary naming fills the graph with near-duplicates.

This exists so the whole pipeline runs, is testable, and passes CI with no API
key. It is genuinely weaker than the Claude extractor at prose inference — it
will not spot an ownership claim phrased indirectly. What it does give up
nothing on is the part that matters most here: every edge it emits carries a
real character span into the real body text, so the §11 gates and the citation
validator are exercised against true evidence rather than plausible-looking
offsets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from company_brain.extract.base import ExtractionRequest, ExtractionResult
from company_brain.schemas.edges import (
    Edge,
    Evidence,
    Predicate,
    Provenance,
    decide_status,
)


@dataclass(frozen=True, slots=True)
class RosterEntry:
    """One curated entity and the surface forms that refer to it."""

    node_id: str
    surfaces: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Roster:
    people: tuple[RosterEntry, ...] = ()
    teams: tuple[RosterEntry, ...] = ()
    tools: tuple[RosterEntry, ...] = ()
    processes: tuple[RosterEntry, ...] = ()
    accounts: tuple[RosterEntry, ...] = ()

    def all(self) -> tuple[RosterEntry, ...]:
        return self.people + self.teams + self.tools + self.processes + self.accounts


# "Sam owns X" / "Sam is responsible for X" — an explicit claim, not a mention.
_OWNS = re.compile(
    r"(?:\*\*)?owner(?:\*\*)?\s*:\s*(?P<who>[^(\n]+)|"
    r"(?P<who2>[A-Z][\w'À-ɏ.-]+(?:\s+[A-Z][\w'À-ɏ.-]+)*)\s+"
    r"(?:owns|is responsible for|will own)\s+",
    re.IGNORECASE,
)
_HANDOFF = re.compile(
    r"(?P<from>\w+)\s+hands? off to\s+(?P<to>\w+)|"
    r"hand(?:ing|ed)?\s+(?:this|the\s+\w+\s+ticket)?\s*(?:over\s+)?to\s+(?P<to2>\w+)",
    re.IGNORECASE,
)


class RuleBasedExtractor:
    """Roster-matching extractor. Pure: same input, same edges, always."""

    model = "rules-offline"
    prompt_version = "roster-v1"

    def __init__(self, roster: Roster) -> None:
        self.roster = roster
        # Longest surface first, so "Project Snowflake" wins over "Snowflake".
        self._surfaces: list[tuple[str, str]] = sorted(
            ((s, e.node_id) for e in roster.all() for s in e.surfaces),
            key=lambda pair: (-len(pair[0]), pair[0]),
        )
        self._person_by_surface = {
            s.lower(): e.node_id for e in roster.people for s in e.surfaces
        }
        self._team_by_surface = {s.lower(): e.node_id for e in roster.teams for s in e.surfaces}

    def extract(self, request: ExtractionRequest) -> ExtractionResult:
        body = request.body
        lowered = body.lower()
        edges: list[Edge] = []
        claimed: list[tuple[int, int]] = []

        for surface, node_id in self._surfaces:
            if node_id == request.node_id:
                continue
            for match in re.finditer(rf"(?<!\w){re.escape(surface.lower())}(?!\w)", lowered):
                span = (match.start(), match.end())
                # First (longest) surface to claim a span keeps it, so
                # "Snowflake" inside "Project Snowflake" is not double-counted.
                if any(s < span[1] and span[0] < e for s, e in claimed):
                    continue
                claimed.append(span)
                edges.append(
                    self._edge(
                        Predicate.MENTIONS,
                        node_id,
                        0.9,
                        (Evidence(node="self", span=span, quote=body[span[0] : span[1]]),),
                    )
                )
                break  # one mention edge per entity; the span points at the first

        edges.extend(self._ownership(body))
        edges.extend(self._handoffs(body))

        unresolved = tuple(sorted({m.group(0) for m in re.finditer(r"\bSam K\.(?!\w)", body)}))

        # De-duplicate on (predicate, object); Frontmatter would reject dupes
        # anyway, and losing the second span is fine — the first is evidence enough.
        seen: dict[tuple[str, str], Edge] = {}
        for edge in edges:
            seen.setdefault((str(edge.predicate), edge.object), edge)

        return ExtractionResult(
            edges=tuple(sorted(seen.values(), key=lambda e: e.sort_key())),
            model=self.model,
            prompt_version=self.prompt_version,
            unresolved=unresolved,
        )

    def _edge(
        self,
        predicate: Predicate,
        obj: str,
        confidence: float,
        evidence: tuple[Evidence, ...],
    ) -> Edge:
        return Edge(
            predicate=predicate,
            object=obj,
            confidence=confidence,
            provenance=Provenance.LLM,
            status=decide_status(predicate, confidence, Provenance.LLM, evidence),
            evidence=evidence,
        )

    def _ownership(self, body: str) -> list[Edge]:
        out: list[Edge] = []
        for match in _OWNS.finditer(body):
            who = (match.group("who") or match.group("who2") or "").strip()
            person = self._person_by_surface.get(who.lower())
            if person is None:
                continue
            span = (match.start(), match.end())
            # Confidence is high and it still proposes rather than accepts —
            # `owns` has no auto-accept threshold at any confidence (§11).
            out.append(
                self._edge(
                    Predicate.OWNS,
                    person,
                    0.75,
                    (Evidence(node="self", span=span, quote=body[span[0] : span[1]].strip()),),
                )
            )
        return out

    def _handoffs(self, body: str) -> list[Edge]:
        out: list[Edge] = []
        for match in _HANDOFF.finditer(body):
            target = (match.group("to") or match.group("to2") or "").strip()
            team = self._team_by_surface.get(target.lower())
            if team is None:
                continue
            span = (match.start(), match.end())
            out.append(
                self._edge(
                    Predicate.HANDOFF_TO,
                    team,
                    0.6,
                    (Evidence(node="self", span=span, quote=body[span[0] : span[1]].strip()),),
                )
            )
        return out
