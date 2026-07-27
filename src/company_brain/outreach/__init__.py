"""Outreach: turning what the graph knows about a person into a reviewed draft.

Two things this package deliberately does *not* do.

**It never writes to the graph.** An outreach draft is not a claim about the
company, so accepting one must not produce a node or an edge. That is why the
drafts live in their own store rather than in ``review/proposals.py``, whose
``apply()`` is documented as the only path from a proposal into the canonical
markdown. Reusing it would have meant special-casing that guarantee away.

**It never sends email.** ``lead.py`` resolves a person to a lead record and
stops there; ``drafts.py`` records that a human approved a message and that it
was dispatched. No outbound message leaves this system today, and the dispatch
path says so rather than implying otherwise — see :func:`drafts.OutreachStore.dispatch`.
"""
