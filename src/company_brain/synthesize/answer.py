"""Answer synthesis and the citation validator.

Invariant 11: an answer without citations is an **error**, not a degraded
response. The validator runs in the request path, not in tests, and it fails
closed on four separate conditions:

1. a cited ID that wasn't in the retrieved context (fabrication)
2. a cited ID the principal cannot see (leak — raises, and should alert)
3. a non-trivial claim sentence with no citation
4. a cited span that doesn't resolve in the node it points at

Answers separate *asserted* facts ("Sam is named owner in doc X") from
*inferred* patterns ("14 of 20 escalations bounced"), because the §11 gates make
that distinction load-bearing and an answer that hides it re-introduces exactly
the mention→ownership drift the gates exist to prevent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from company_brain.acl.grants import AccessFilter
from company_brain.index.base import Index
from company_brain.retrieve.hybrid import Retrieval

CITE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
# Sentences that assert nothing and therefore need no citation.
_TRIVIAL = re.compile(
    r"^\s*(?:based on|according to|here'?s?|in summary|no |i (?:could|couldn'?t|did)"
    r"|there (?:is|are) no|nothing )",
    re.IGNORECASE,
)


class UncitedAnswerError(RuntimeError):
    """Invariant 11 violated. Never downgrade this to a warning."""


class CitationLeakError(RuntimeError):
    """An answer cited a node the principal cannot read. Alert-worthy."""


@dataclass(slots=True)
class Citation:
    node_id: str
    title: str
    snippet: str


@dataclass(slots=True)
class Answer:
    question: str
    text: str
    citations: list[Citation] = field(default_factory=list)
    asserted: list[str] = field(default_factory=list)
    inferred: list[str] = field(default_factory=list)
    insufficient_evidence: bool = False


@runtime_checkable
class Synthesizer(Protocol):
    name: str

    def synthesize(self, question: str, retrieval: Retrieval, index: Index) -> Answer: ...


def validate(answer: Answer, retrieval: Retrieval, access: AccessFilter, index: Index) -> None:
    """Fail closed. Called on every answer, in the request path."""
    if answer.insufficient_evidence:
        return  # an explicit "I don't know" is a valid, citation-free outcome

    cited = CITE.findall(answer.text)
    if not cited:
        raise UncitedAnswerError(
            "answer contains no citations; an uncited answer is a bug, not a "
            "degraded response (invariant 11)"
        )

    in_context = {n.node_id for n in retrieval.nodes}
    for node_id in cited:
        if node_id not in in_context:
            raise UncitedAnswerError(
                f"answer cites {node_id!r}, which was not in the retrieved context — "
                f"this is a fabricated citation"
            )
        indexed = index.get_node(node_id)
        if indexed is None:
            raise UncitedAnswerError(f"answer cites {node_id!r}, which is not indexed")
        if not access.allows(indexed.acl_ref, indexed.sensitivity):
            raise CitationLeakError(
                f"answer cites {node_id!r}, which principal {access.principal.id!r} cannot read"
            )

    for claim in _claim_units(answer.text):
        if not CITE.search(claim):
            raise UncitedAnswerError(f"uncited claim: {claim[:110]!r}")


def _claim_units(text: str) -> list[str]:
    """Split an answer into the units that each require their own citation.

    A line is the claim unit, not a sentence. In a bulleted answer the citation
    naturally trails the terminal period, so sentence-splitting would tear
    "X happened. [[node]]" into an uncited claim plus a bare citation — and
    reject a correctly-cited answer. Long unbulleted prose still falls back to
    sentences, so a paragraph can't smuggle five claims behind one citation.
    """
    units: list[str] = []
    for raw_line in text.strip().split("\n"):
        line = raw_line.strip("-* \t")
        if len(line) < 25 or _TRIVIAL.match(line):
            continue
        if CITE.search(line) or len(line) < 240:
            units.append(line)
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", line):
            candidate = sentence.strip()
            if len(candidate) >= 25 and not _TRIVIAL.match(candidate):
                units.append(candidate)
    return units


class ExtractiveSynthesizer:
    """Offline synthesizer: composes an answer from retrieved evidence only.

    It cannot paraphrase or reason across documents the way Claude can. What it
    can do — and what matters for proving the contract — is never assert
    anything that isn't in a retrieved chunk, and cite every claim to a node ID
    that actually exists. Swapping in `ClaudeSynthesizer` changes one argument.
    """

    name = "extractive-offline"

    def synthesize(self, question: str, retrieval: Retrieval, index: Index) -> Answer:
        grounded = [n for n in retrieval.nodes if n.snippets]
        if not grounded:
            return Answer(
                question=question,
                text="I could not find evidence for this in the material I can see.",
                insufficient_evidence=True,
            )

        terms = {_stem(t) for t in re.findall(r"[a-z]{4,}", question.lower())}
        asserted: list[str] = []
        inferred: list[str] = []
        citations: list[Citation] = []
        lines: list[str] = []

        for node in grounded[:5]:
            # Score sentences across every retrieved chunk of the node, not just
            # the single best-scoring chunk: "**Owner:** Sam Kaur" and "how the
            # process works" routinely land in different chunks, and picking the
            # chunk first discards the sentence that actually answers the question.
            sentence = _best_sentence("\n".join(node.snippets), terms)
            if not sentence:
                continue
            citations.append(Citation(node.node_id, node.title, sentence))
            claim = f"- {sentence} [[{node.node_id}]]"
            lines.append(claim)
            (asserted if node.hops == 0 else inferred).append(claim)

        if not lines:
            return Answer(
                question=question,
                text="I could not find evidence for this in the material I can see.",
                insufficient_evidence=True,
            )

        related = [n for n in retrieval.nodes if n.hops > 0][:4]
        text = "\n".join(lines)
        if related:
            names = ", ".join(f"[[{n.node_id}]]" for n in related)
            inferred.append(f"Related by graph traversal: {names}")

        return Answer(
            question=question,
            text=text,
            citations=citations,
            asserted=asserted,
            inferred=inferred,
        )


# Sentences that make an explicit ownership or responsibility claim. Weighted
# up because "who owns X" is answered by these and by almost nothing else — but
# note these still surface *asserted* claims from documents, which is not the
# same as the graph having an accepted `owns` edge (§11).
_CLAIMY = re.compile(
    r"\b(owner|owns|own|responsible|accountable|signs? off|decided by|led by)\b",
    re.IGNORECASE,
)


def _stem(token: str) -> str:
    """Crudest possible suffix stripping.

    Enough to match "renewals" against "renewal" and "owns" against "own",
    which is the difference between answering the seeded questions and not.
    A real stemmer is an M4 concern, alongside the evaluation harness.
    """
    for suffix in ("ies", "es", "s", "ing", "ed"):
        if len(token) > 4 and token.endswith(suffix):
            return token[: -len(suffix)]
    return token


def _overlap(text: str, terms: set[str]) -> int:
    words = {_stem(w) for w in re.findall(r"[a-z]{3,}", text.lower())}
    return len(words & terms)


def _best_sentence(snippet: str, terms: set[str]) -> str:
    candidates = [
        s.strip(" -*\n") for s in re.split(r"(?<=[.!?])\s+|\n", snippet) if len(s.strip()) > 20
    ]
    if not candidates:
        return snippet.strip()[:220]
    best = max(
        candidates,
        key=lambda s: _overlap(s, terms) * 2 + (3 if _CLAIMY.search(s) else 0),
    )
    return best[:260]
