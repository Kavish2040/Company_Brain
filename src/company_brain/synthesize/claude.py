"""Claude-backed synthesis.

The contract is unchanged from the offline synthesizer: every claim carries a
`[[node_id]]` citation, and the validator in `answer.py` still runs afterwards
and still fails closed. Nothing here is trusted — the model is asked to cite,
and then its output is checked against the retrieved context, the principal's
visible set, and the index.

What Claude adds over the extractive path is the ability to *answer the question
asked* rather than surface the most lexically similar sentence, and to say
plainly when the retrieved material does not contain an answer.
"""

from __future__ import annotations

import os
import re

import anthropic

from company_brain.index.base import Index
from company_brain.retrieve.hybrid import Retrieval
from company_brain.synthesize.answer import Answer, Citation

DEFAULT_MODEL = "claude-opus-5"
NO_ANSWER = "INSUFFICIENT_EVIDENCE"

SYSTEM = f"""\
You answer questions about a company from retrieved excerpts. You have no
knowledge of this company beyond what is given to you in the context block.

Citation format, non-negotiable:
- Every sentence that makes a factual claim ends with [[node_id]], using an id
  from the context exactly as written.
- Never cite an id that is not in the context. There is a validator; a
  fabricated id fails the request outright rather than degrading the answer.
- One claim per line, as a `- ` bullet, with its citation at the end of the line.
- No headings, no section labels, no bare lines. A line like
  "Support -> Engineering handoff" asserts nothing and cannot be cited, so the
  validator rejects the whole answer and the user sees nothing. Put the label
  inside the claim instead.
- A claim about *absence* still needs citations — cite the documents you
  checked: "no document describes X [[a]] [[b]]".

Distinguish assertion from inference:
- If a document states something directly, say so plainly.
- If you are inferring across documents, say "this suggests" or similar, and
  cite every document the inference rests on.
- Being quoted about a topic is not the same as owning it. Do not upgrade a
  mention into an ownership claim.

If the context does not answer the question, reply with exactly {NO_ANSWER} and
nothing else. Saying you don't know is a correct answer; guessing is not. The
context is filtered by the reader's permissions, so material may be missing —
never speculate about what you cannot see."""


class ClaudeSynthesizer:
    name = "claude"

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        client: anthropic.Anthropic | None = None,
        max_tokens: int = 2048,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.client = client or anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def synthesize(self, question: str, retrieval: Retrieval, index: Index) -> Answer:
        grounded = [n for n in retrieval.nodes if n.snippets][:10]
        if not grounded:
            return Answer(
                question=question,
                text="I could not find evidence for this in the material I can see.",
                insufficient_evidence=True,
            )

        context = "\n\n".join(
            f"[[{node.node_id}]] {node.title}\n" + "\n".join(node.snippets[:3])
            for node in grounded
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n\n{context}\n\n---\n\nQuestion: {question}",
                }
            ],
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()

        if NO_ANSWER in text:
            return Answer(
                question=question,
                text="The material I can see does not answer this.",
                insufficient_evidence=True,
            )

        cited_ids = set(re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", text))
        citations = [
            Citation(node.node_id, node.title, node.snippets[0][:300])
            for node in grounded
            if node.node_id in cited_ids
        ]
        # asserted vs inferred is derived from hop distance, not from the
        # model's own framing — a seed document said it, an expanded one is
        # something we reached by traversal (§7).
        seeds = {n.node_id for n in grounded if n.hops == 0}
        lines = [line for line in text.split("\n") if line.strip()]
        return Answer(
            question=question,
            text=text,
            citations=citations,
            asserted=[ln for ln in lines if any(f"[[{s}]]" in ln for s in seeds)],
            inferred=[ln for ln in lines if not any(f"[[{s}]]" in ln for s in seeds)],
        )
