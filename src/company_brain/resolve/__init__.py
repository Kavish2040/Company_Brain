"""Entity resolution, layer 3 (docs/ARCHITECTURE.md §10).

Blocked candidate generation, scored matching, `same_as` proposals with
evidence, and reversible merges. Layers 1 and 2 (identity keys, curated
aliases) live in the connectors and on entity pages; layer 4 is the extractor's
refusal to guess. This package is only the layer that is allowed to be wrong,
which is why it terminates in a proposal rather than a mutation.

    resolver.Layer3Resolver       profile -> block -> score -> propose
    proposals.SameAsProposalStore write / read / decide, under store/_proposals/
    merge.Merger                  apply and reverse a human-decided merge
    merge.ReviewWorkflow          accept, reject, revert — all invertible

Nothing here mutates the graph on its own. `Merger` is called only by
`ReviewWorkflow`, and only in response to a human decision.

--------------------------------------------------------------------------
Wiring this work does not do, on purpose
--------------------------------------------------------------------------

`app.py`, `cli/main.py`, `index/`, `review/` and `connectors/` are owned by other
sessions, so this package is deliberately unwired. What it wants, in priority
order:

0. **Converge on `review/proposals.py`.** That module landed while this one was
   being written and is the better long-term home: content-addressed proposal
   IDs, a JSON queue-row sidecar carrying `decided_by` and `decided_at`, a
   `base_sha256` staleness check, and a line-level diff view. `SameAsProposal`
   should become a third `ProposalKind` there rather than a parallel store. It
   is not done here for two reasons, both needing a decision rather than a
   patch: `ProposalKind` has no merge variant, and `ProposalStore.apply` writes
   *one* node into the graph, whereas accepting a merge is two coordinated
   writes plus a tombstone. Adding a kind whose apply path is not "put this
   node" is a change to the shape of their abstraction, not an addition to it.
   Until then the two stores are disjoint by construction and neither breaks
   the other: theirs scans `_proposals/*.json` and ignores loose markdown; this
   one filters `walk_proposal_ids()` on the `same-as-` prefix. The local types
   are named `SameAsProposalStore` / `SameAsProposalError` so the collision with
   `review.proposals.ProposalStore` is visible rather than merely legal.
1. **`cb resolve`** in `cli/main.py`: run `Layer3Resolver`, print
   `ResolutionReport.summary()`, and `SameAsProposalStore.write_all` the result.
   Writing proposals is the *only* write; there is no flag that merges.
2. **`cb review` sees these proposals.** `ReviewQueue.pending_edges` walks the
   graph, and `Repository.walk` skips `_proposals/` by design, so today the two
   queues are disjoint. `SameAsProposalStore.pending()` already returns
   `review.queue.PendingEdge`, so the join is one extra loop in
   `ReviewQueue.pending_edges` over `walk_proposal_ids()` — a change in a file
   this work does not own. Subsumed by item 0 if that happens first.
3. **`build_app` exposes a resolver** the way it exposes `index` and `grants`,
   so the MCP server and the API share one configuration (the composition-root
   rule in CLAUDE.md).

--------------------------------------------------------------------------
Flagged — §10 open questions that block, or that this design pushes into view
--------------------------------------------------------------------------

**A. `Provenance` has no value for a deterministic derivation.** A layer-3 match
is neither `structural` (it is inferred, not source metadata), nor `human`, nor
`llm` (no model runs; the scorer is a pure function). It is written as `llm`
because that is the only value the §11 gate table actually gates — `structural`
and `human` are auto-accepted by `decide_status`, which would auto-merge people
and is forbidden by §10.2. The cost is real: `ReviewQueue.accept_rate` filters
to `provenance == "llm"` to measure whether the *model's* gates are calibrated,
and layer-3 volume now pollutes that number. Wanted: a fourth value,
`Provenance.DERIVED`, gated like `llm` and counted separately. Needs a change to
`schemas/edges.py`.

**B. No *edge* can record who decided.** ROADMAP M3's demo asks for "the
reviewer's name on the provenance", and `Provenance` is a three-value enum with
no room for a principal. `review/proposals.py` has since answered the audit half
of this — `ProposalRecord` carries `decided_by` and `decided_at` in a sidecar,
which is the right place for it — and converging (item 0 above) would let this
module drop its own decision fence. What is still open is narrower and still
real: the accepted `same_as` edge that lands in the graph carries
`provenance: human` and nothing else, so reading the *store* alone cannot tell
you which human. That is a `schemas/edges.py` decision.

**C. A merged node is still fully indexed and retrievable.** `App.load_index`
indexes every node `repo.walk()` yields regardless of `status`, and
`retrieve/hybrid.py` does not filter on it either. Because a merge here
preserves the losing node's body (it must, or unmerge cannot be exact), an
accepted merge currently leaves *both* records searchable — the duplicate the
merge was supposed to resolve still surfaces in `cb ask`. The fix is one
condition in `App.load_index` or `MemoryIndex.rebuild`: skip `status: merged`
nodes, or index them as an alias of their redirect target. Both files are owned
elsewhere. Until then a merge is correct in the store and invisible in
retrieval, which is the wrong half to have working.

**D. Should a `merged` node be editable in the live collaboration surface?**
`collab/` lets a human edit any entity page's body. Editing a merged stub
between the merge and an unmerge makes the unmerge non-exact — not incorrect,
but no longer byte-identical, which is the criterion this milestone is judged
on. Proposal: `collab/guard.py` refuses edits to a node whose status is not
`active`. Owned elsewhere; not done here.

**E. Process and Decision resolution is not implemented.** §10.3 asks for
embedding-plus-participant clustering with a human naming pass, not pairwise
string matching, and it needs the embedder from `index/`. `ResolutionReport`
counts these nodes and says so rather than leaving them silently unresolved.
Blocked behind question 6 in §14 — who the reviewer persona is — because
clustering several hundred process mentions is either a twenty-minute ops task
or an impossible ask of an executive, and that decides the cluster size to aim
for.

**F. `Account` versus `Person` is enforced but not resolved.** Different node
types never pair here, so `support@meridian.example` can never be merged into a
person — correct per §10.2. What §10.2 also asks for, and this does not do, is
*proposing* `operated_by` edges from an account to the people who post as it.
That is a different predicate with a different gate and its own failure mode
(everyone who ever answers from a shared inbox looks like its operator); it
needs a policy decision before it is worth building.
"""

from __future__ import annotations

from company_brain.resolve.blocking import (
    Blocking,
    BlockKey,
    CandidatePair,
    block,
    blocking_keys,
)
from company_brain.resolve.keys import identity_conflict, identity_keys
from company_brain.resolve.merge import MergeError, Merger, MergeRecord, ReviewWorkflow
from company_brain.resolve.profiles import (
    RESOLVABLE_TYPES,
    EntityProfile,
    build_profiles,
)
from company_brain.resolve.proposals import (
    SameAsProposal,
    SameAsProposalError,
    SameAsProposalStore,
)
from company_brain.resolve.resolver import Layer3Resolver, ResolutionReport
from company_brain.resolve.scoring import Component, Policy, ScoreCard, Weights, score_pair

__all__ = [
    "RESOLVABLE_TYPES",
    "BlockKey",
    "Blocking",
    "CandidatePair",
    "Component",
    "EntityProfile",
    "Layer3Resolver",
    "MergeError",
    "MergeRecord",
    "Merger",
    "Policy",
    "ResolutionReport",
    "ReviewWorkflow",
    "SameAsProposal",
    "SameAsProposalError",
    "SameAsProposalStore",
    "ScoreCard",
    "Weights",
    "block",
    "blocking_keys",
    "build_profiles",
    "identity_conflict",
    "identity_keys",
    "score_pair",
]
