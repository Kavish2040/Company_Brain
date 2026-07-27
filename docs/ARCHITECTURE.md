# company_brain — Architecture

Status: **proposal, awaiting review**. Nothing here is implemented.

This document decides the things that are expensive to change later: the on-disk
format, the identity/ID scheme, the permission model, and the boundary between
deterministic and model-generated content. It records rejected alternatives
alongside the choices, because in most cases the rejected option was reasonable
and we may want to revisit it.

§4.1 was an open question and is now **resolved against the live API** — the
measured result contradicts the documented one, so read that table before
touching `extract/`.

Three items the kickoff asked me to flag rather than solve are in
[§10 Entity resolution](#10-entity-resolution-flagged),
[§9.3 Upstream deletes and edits](#93-upstream-deletes-and-edits), and
[§11 Where extraction needs a human](#11-where-extraction-needs-a-human-flagged).

---

## 1. System overview

```
                 ┌─────────────────────────────────────────────┐
  sources        │  connectors: fs, slack, gdrive, gmail, ...   │
                 └──────────────────┬──────────────────────────┘
                                    │ raw bytes + source metadata + ACL ref
                 ┌──────────────────▼──────────────────────────┐
  normalize      │  pure(source bytes, normalizer version)      │  DETERMINISTIC
                 │  → markdown body + structural frontmatter    │
                 └──────────────────┬──────────────────────────┘
                                    │
                 ┌──────────────────▼──────────────────────────┐
  extract        │  LLM: entities, typed edges, evidence spans  │  CACHED
                 │  → relations block + generated regions       │  (see §4)
                 └──────────────────┬──────────────────────────┘
                                    │
     ╔══════════════════════════════▼══════════════════════════╗
     ║   MARKDOWN STORE  —  canonical, human-editable, git      ║
     ║   store/documents/…  store/people/…  store/processes/…   ║
     ╚══════════════════════════════┬══════════════════════════╝
                                    │ one-way projection, fully rebuildable
                 ┌──────────────────▼──────────────────────────┐
  index          │  Postgres: nodes, edges, chunks, pgvector,   │
                 │  FTS, acl_grants, review_queue               │
                 └──────────────────┬──────────────────────────┘
                                    │ every query carries a Principal
        ┌───────────────┬───────────┴───────────┬────────────────┐
        ▼               ▼                       ▼                ▼
    CLI `ask`      FastAPI HTTP            MCP server       review CLI/UI
                                        (agents; writes →
                                         proposals, not graph)
```

Two invariants define the shape of everything below:

1. **Markdown is the database.** Postgres is a cache with a query planner. If they
   disagree, Postgres is wrong and gets rebuilt.
2. **Every read path is parameterised by a principal.** There is no unauthenticated
   read of node content anywhere in the system, including inside the retrieval
   pipeline's own intermediate steps.

---

## 2. The canonical store

### 2.1 Layout

```
store/
  public/
    documents/gdrive/vendor-renewal-policy-4d20be.md
    tools/netsuite.md
  internal/
    documents/slack/2024/03/eng-standup-2024-03-14-a91f3c.md
    documents/email/re-netsuite-renewal-thread-77c0a1.md
    people/sam-kaur.md
    teams/support.md
    processes/vendor-renewal.md
    decisions/2024-03-adopt-netsuite-4e91.md
  restricted/
    documents/slack/2024/03/comp-planning-2024-03-02-1d84f7.md
  _proposals/                      # agent + low-confidence writes, not yet graph
  _cache/extraction/<key>.json     # committed; see §4
```

**The first segment is the sensitivity tier, and it is load-bearing** — §6.2. A node's
path is `<tier>/<node_id>.md`, the tier is written from `acl.sensitivity`, and a
repository pinned to one tier refuses everything else (`TierMismatchError`) rather than
writing it somewhere merely mislabelled. In production each root is its own bucket with
its own IAM (`TieredBackend`), so a credential scoped to `internal` cannot read a
restricted node even if a bug asks it to; the tier segment stays in the key so a dev
subtree and the bucket it is promoted into hold identical paths.

Everything *below* the tier is for humans, and is not load-bearing: the index is built
by walking the tree, not by parsing paths. Node IDs are unchanged and carry no tier —
a document reclassified from `internal` to `restricted` keeps its ID and moves roots
(invariant 12 is about identity, not location).

The workflow trees sit beside the tier roots rather than inside them, which is what
excludes them from a node walk structurally instead of by a denylist. Two of them —
`_proposals/` and `_cache/extraction/` — hold content derived from nodes and are
therefore **not yet tier-partitioned when they should be**; see §6.2. `_sync/` holds
cursors and ID sets only. There is no `_tombstones/`: a delete rewrites the node in
place (§9.3), so a tombstone lives at its own ID, in its own tier root.

### 2.2 Node IDs

**ID = `<type_plural>/<slug>`**, identical to the path minus `store/` and `.md`.

- Entity slugs are human-chosen and stable: `people/sam-kaur`.
- Document slugs are `<derived-title>-<hash6>` where `hash6` is the first 6 hex
  chars of `blake2b(canonical_source_uri)`. The title half gives readability; the
  hash half gives stability under retitling and collision safety.

IDs are **immutable**. Renaming a person's page is a two-step operation: write the
new node, leave a tombstone stub at the old ID with `redirects_to`. Old citations
never break — an answer generated last quarter must still resolve.

> **Rejected:** opaque ULIDs as IDs (`doc_01J8…`). Better for rename-freedom, but it
> makes the repo unreadable in an editor, which the kickoff names as a hard
> requirement. We take the rename cost.
>
> **Rejected:** pure title slugs with no hash. Two `meeting-notes.md` from different
> sources collide, and the collision resolution (`-2`) is order-dependent, which
> breaks determinism.

### 2.3 File format

````markdown
---
id: documents/slack/2024/03/eng-standup-2024-03-14-a91f3c
type: Document
title: "Eng standup — 2024-03-14"
source:
  connector: slack
  uri: slack://T01ABC/C0ENG/p1710403200000100
  external_id: "1710403200.000100"
  external_version: "1710403200.000100"   # etag / revisionId / message edit ts
  content_sha256: 3f2a9c…
acl:
  ref: slack:channel:C0ENG                 # see §6 — a reference, not a list
  sensitivity: internal
authors: [people/sam-kaur]
timestamps:
  created: 2024-03-14T09:00:00Z            # from the SOURCE, never wall-clock
  modified: 2024-03-14T09:31:00Z
normalizer: { name: slack_export, version: 1.0.0 }
extraction:
  model: claude-sonnet-5
  prompt_version: entity-v3
  cache_key: b7c1e0…
  status: accepted                         # accepted | partial | proposed
relations:
  - predicate: authored_by
    object: people/sam-kaur
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.94
    provenance: llm
    evidence: { node: self, span: [412, 431] }
    status: accepted
  - predicate: handoff_to
    object: teams/finance
    confidence: 0.61
    provenance: llm
    evidence: { node: self, span: [980, 1104] }
    status: proposed                       # NOT in the graph until reviewed
---

Sam raised that the [[tools/netsuite|NetSuite]] renewal lands in April and that
Finance has not been looped in yet.

handoff_to:: [[teams/finance]]
````

Notes on the choices:

- **Edges live in frontmatter; wikilinks live in the body.** The frontmatter
  `relations` block is authoritative — it carries confidence, evidence spans, and
  review status, which a wikilink cannot. Body links are the human/Obsidian surface.
  Ingest of a human-edited file *lifts* body links into `relations` with
  `provenance: human, confidence: 1.0`. A bare `[[…]]` becomes a `mentions` edge; a
  Dataview-style `predicate:: [[…]]` becomes that typed edge.
- **No `ingested_at` in the file.** Wall-clock in a canonical file makes byte-identical
  re-ingestion impossible. Ingestion timestamps live in Postgres `ingest_runs`.
- **`acl.ref`, not an ACL list.** See §6.1.

### 2.4 Generated regions on entity pages

Entity pages (`people/`, `processes/`, …) are synthesized, but humans must be able to
annotate them and not lose the annotation on the next ingest. Machine-owned content
is fenced:

```markdown
## Sam Kaur

Joined 2021. Owns the vendor lifecycle end to end. <!-- human-written, never touched -->

<!-- cb:generated start region=mentions content_hash=9f21ab -->
Mentioned in 34 documents. Most recent: [[documents/…]]
<!-- cb:generated end region=mentions -->
```

Rule: the writer regenerates only the span between fences, and only if the current
content hashes to `content_hash`. If a human edited inside the fence, the write is
diverted to `_proposals/` and surfaced for review rather than clobbering the edit.
Everything outside every fence is untouchable by machine writers, forever.

> **Rejected:** separate `content/` and `annotations/` trees, so generated content is
> physically isolated. Cleaner regeneration story, but you can no longer open one file
> and see the whole picture of a person — which is the point of the product.

---

## 3. Node and edge taxonomy

| Type | Origin | Merged? |
|---|---|---|
| `Document` | 1:1 with a source artifact | no |
| `Person` | synthesized, resolved across sources | yes (§10) |
| `Team` | synthesized | yes |
| `Tool` | synthesized | yes, cautiously |
| `Process` | synthesized, LLM-named | **no auto-merge** (§10.3) |
| `Decision` | extracted from documents | no auto-merge |

Edges: `authored_by`, `mentions`, `owns`, `depends_on`, `handoff_to`, `supersedes`,
plus two internal predicates: `same_as` (entity resolution, reversible) and
`redirects_to` (tombstones).

Every edge carries `provenance ∈ {structural, llm, human}`, `confidence`, `evidence`,
and `status ∈ {accepted, proposed, rejected}`. **Only `accepted` edges are traversed
at query time.** `structural` edges (derived from source metadata, e.g. the Slack
message's author field) are auto-accepted; `llm` edges are governed by §11.

Pydantic models in `schemas/` are the single source of truth for all of the above and
generate the JSON Schema used to validate frontmatter in CI.

---

## 4. Determinism, and the LLM problem

The acceptance criterion — full re-ingestion produces a byte-identical tree — is
achievable for normalization and **not** achievable for extraction. Splitting these
honestly is the most important thing in this document.

**Normalization is a pure function** of `(source bytes, normalizer name+version,
config)`. Enforced by:

- canonical YAML emit (sorted keys, block style, explicit quoting, LF, no trailing
  whitespace, single trailing newline)
- all collections sorted by a declared key before emit
- no wall-clock, no `uuid4`, no `set` iteration in output paths, `PYTHONHASHSEED=0`
- timestamps normalized to UTC RFC-3339 with fixed precision
- normalizer version is part of the frontmatter, so a library upgrade produces a
  visible, reviewable diff rather than silent churn

The last point matters: PDF→markdown output changes across `pdfminer`/`docling`
releases. We pin exactly, record the version in the file, and treat a bump as a
migration with a reviewed diff — not as a routine dependency update.

**Extraction is not pure — and there is no knob to make it so.** This turned out
stronger than originally written. `temperature`, `top_p`, and `top_k` were
*removed* from Claude Opus 5 and Sonnet 5; sending any of them returns a 400.
There is no sampling parameter left to pin, so "set temperature 0 and hope" is
not an available strategy, even a bad one. The cache below is not a convenience;
it is the only mechanism by which re-ingestion can be reproducible.

> Extraction results are content-addressed and cached in `store/_cache/extraction/`,
> **and the cache is committed to the repo.** Cache key =
> `blake2b(content_sha256 ‖ prompt_version ‖ model_id ‖ decode_params)`.

Re-ingestion with a warm cache is deterministic and byte-identical. A cache miss is
an explicit event: it appears in `ingest_runs`, and `company_brain ingest --frozen`
(the mode CI uses) **fails** on a miss rather than calling the model. This makes the
acceptance test real: it tests our pipeline, not the provider's mood.

Cost: the cache is repo state that must be regenerated on prompt/model changes. That
regeneration is a deliberate, reviewed operation (`extract refresh --prompt-version`),
which is the behaviour we want anyway.

> **Rejected:** re-running extraction on every ingest and asserting only semantic
> equivalence. Semantic-equivalence assertions are themselves flaky and give up the
> git-diffability that makes the markdown store worth having.

### 4.1 Evidence spans — **resolved**

§11 requires every LLM-derived edge to carry an evidence span. Two mechanisms
could supply one:

1. **Structured outputs** (`output_config.format`) — schema-validated extraction
   with no parsing layer, but any span the model reports is self-asserted and
   routinely off by a few characters.
2. **Native citations** (`citations: {enabled: true}` on a document block) —
   returns `cited_text` plus exact `start_char_index` / `end_char_index`
   computed by the API rather than guessed by the model.

These were believed mutually exclusive. Measured against the live API they are
not — the exclusion is narrower than documented:

| shape | result |
|---|---|
| `output_config.format` + citations | **400** — "Citations cannot be enabled when output format is set" |
| forced `tool_choice` + citations | accepted, but returns a lone `tool_use` block; no cited text is emitted, so no spans come back |
| **`tool_choice: auto` + strict tool + citations** | **both** — cited text blocks carrying API-computed offsets, followed by a schema-validated `tool_use` block |

**Decision: the third shape.** `extract/claude.py` asks for prose *and* a tool
call. Citations attach to the prose; the strict tool carries the structure. No
two-pass, no separate reconciliation step.

Two consequences worth keeping:

* An offset is **never** taken from the model. `_match_span` resolves a quote
  against an API-computed citation span, or failing that against a literal
  search of the body we sent. An edge whose quote resolves to neither is
  **dropped**, not recorded — an `Edge` with `llm` provenance and no evidence is
  rejected at construction anyway, and a §11 gate whose evidence a reviewer
  cannot check is not a gate.
* The tool's `object` field is an **enum of curated roster ids**, so the model
  selects entities rather than naming them (§10.3). Measured on the synthetic
  corpus, "Sam K." comes back in `unresolved` rather than being guessed into
  either Sam — the §10.2 trap holds under Claude, not just under the rules.

---

## 5. The derived index

Postgres 16 + pgvector. Tables:

```
sources(id, connector, config_hash, last_cursor)
nodes(id PK, type, title, acl_ref, sensitivity, content_sha256,
      source_uri, created_at, modified_at, status, path)
edges(subject, predicate, object, confidence, provenance, status,
      evidence jsonb, PRIMARY KEY (subject, predicate, object))
chunks(id, node_id, ordinal, heading_path, text, token_count, acl_ref)
embeddings(chunk_id PK, model, vec vector(1024))
chunks_fts(chunk_id, tsv tsvector)
principals(id, kind, display, external_ids jsonb)
principal_groups(principal_id, group_id)      -- transitively expanded
acl_grants(acl_ref, principal_id, mode, synced_at)
ingest_runs(id, started_at, connector, files_seen, cache_misses, …)
review_queue(id, kind, payload jsonb, state, created_by, decided_by, decided_at)
extraction_cache_index(key, node_id, model, prompt_version)
```

`acl_ref` is denormalized onto `nodes`, `chunks`, and (implicitly) `embeddings`
specifically so the permission filter is a single indexed predicate in the same query
as the vector search. Duplication is deliberate.

**Rebuild contract.** `company_brain index rebuild --from-scratch` drops and rebuilds
every table above except `principals`/`acl_grants` (which are synced from source
systems, not derived from markdown) and `review_queue` (which is workflow state).
This path runs in CI on every PR against the synthetic corpus — it is not a
break-glass script.

**Drift detection.** `company_brain doctor` compares `nodes.content_sha256` against
the on-disk files and reports: index-ahead (a file was reverted), index-behind (a
file changed without reindex), and orphans. Non-zero exit. Intended for a cron in
prod and a pre-commit hook in dev.

> **Rejected:** a dedicated vector database (Qdrant/Weaviate/Turbopuffer). Better ANN
> ergonomics, but it splits the index into two stores with two rebuild paths and
> makes the ACL join a cross-store operation — exactly the thing that must never be
> approximate. Revisit past ~50M chunks; we are three orders of magnitude away.
>
> **Rejected:** generating the SQL schema from Pydantic models. Tempting given
> "Pydantic is the source of truth", but the storage schema needs indexes, partial
> indexes, and partitioning that have no place in a domain model. Pydantic owns the
> domain; Alembic migrations own the storage. Duplication is checked by a test that
> round-trips every model through the tables.

---

## 6. Permissions

### 6.1 Model

A node's ACL is a **reference to the source system's ACL object**, not a copy of its
membership:

```
node.acl_ref = "slack:channel:C0ENG"
             | "slack:dm:D01XYZ"
             | "gdrive:file:1a2b3c"
             | "gdrive:drive:0AB…"
             | "fs:corpus:public"
```

Membership lives in `acl_grants`, refreshed by connectors. Query filter:

```sql
WHERE n.acl_ref = ANY (cb_visible_refs(:principal_id))
```

`cb_visible_refs` expands group membership through `principal_groups` and is cached
per request.

Why a reference and not a materialized principal list per node: when someone leaves a
Slack channel, we update one row in `acl_grants`. The alternative rewrites every
markdown file that channel produced — a corpus-wide rewrite triggered by an ordinary
HR event, and one that pollutes git history with permission churn.

> **Rejected:** materialized `allowed_principals: [...]` in frontmatter. Simplest
> possible filter, and self-describing in the editor. Rejected on the rewrite-storm
> argument above, plus it puts the org chart in every file.

### 6.2 What the markdown store is *not*

**The markdown store is not a permission boundary.** Anyone with filesystem or repo
access reads everything, including the private DM. The enforcement boundary is the
API/MCP/CLI layer. This needs to be said out loud because the "just open it in
Obsidian" affordance actively encourages handing people the repo.

Consequences we should accept now:

- Each root is classified at the **maximum** sensitivity of anything in it. Tiering is
  what stops that maximum from being the whole corpus's maximum.
- Dev machines get the synthetic corpus, never a production store.
- Sensitivity tiers are **physically separated** into distinct store roots
  (`public/`, `internal/`, `restricted/`), which in production are distinct buckets
  with distinct IAM. A tier is the coarse-grained boundary; `acl_ref` is the
  fine-grained one within a tier. This also gives us the ANN partitioning in §6.4.
- Connectors must be able to refuse: a `restricted` source cannot be ingested into a
  store root that is not `restricted`. Enforced in the writer, not by convention.

#### 6.2.1 How the tier boundary is actually enforced

Three mechanisms, in `store/`:

- **Placement.** `Repository.put` writes to `<tier>/<node_id>.md`, where the tier comes
  from the node's own `acl.sensitivity`. There is no path by which a caller chooses the
  root; the content chooses it.
- **Pinning.** `Repository(backend, tier=…)` refuses any node of another tier with
  `TierMismatchError`, *before* the write. This is the production configuration — one
  repository per root — and it is what makes "structurally unable to write a restricted
  source into a non-restricted root" true rather than aspirational. The bytes never
  land; they are not written somewhere and relabelled.
- **Routing.** `TieredBackend` maps the leading path segment to a per-tier backend, so
  in a deployment the boundary is a credential rather than a directory name.

**Reclassification is the interesting case, and it is where a naïve tiering leaks.**
When a channel goes from `internal` to `restricted`, writing the new node into
`restricted/` is not enough — yesterday's copy is still sitting in `internal/`, still
readable by everyone with internal access, forever. So a write into a stricter root
first clears the looser ones, and a write into a looser root clears the stricter ones
after. There is no atomic rename between buckets, so the ordering is chosen by which
half-done state is survivable: an interrupted *narrowing* leaves the node missing,
which is loud and self-healing on the next sync; an interrupted *widening* leaves a
duplicate whose stale copy is in the stricter root, which is safe. The state we never
reach is a stale copy in a root looser than the node now belongs to. Enumeration raises
`DuplicateNodeError` on either leftover rather than picking one, so a half-done move
surfaces at the next `cb doctor` or index rebuild instead of becoming permanent.

Only an unpinned repository can do this, because no single bucket can see both sides of
the move. That is the honest cost of per-bucket separation: tier migration needs a
component holding all three roots, and in production that component is more privileged
than anything else in the system.

**Two gaps, stated rather than glossed.** `_proposals/` and `_cache/extraction/` hold
content derived from nodes — a proposal quoting a restricted document, an extraction
result carrying its evidence spans — and both currently live in a single root shared by
every tier. Invariant 6 says a derived artifact inherits its narrowest input; these two
trees do not yet honour that *physically*, only in frontmatter. They must be partitioned
before a production store exists. `_sync/` is fine as it is: cursors and external ID
sets, no content.

### 6.3 Derived nodes and ACL propagation

An entity page for Sam aggregates evidence from documents Sam appears in, some of
which are private. Three options:

1. **Intersection of contributor ACLs** — correct but useless; one DM collapses the
   page to the DM's audience.
2. **Union** — leaks by construction. Never.
3. **Per-edge ACL + read-time projection** — each edge inherits the `acl_ref` of its
   *evidence* node. The canonical entity page on disk is the superset (the
   "everything" view). `read_node` assembles the response from only the edges visible
   to the caller, and generated regions are rendered per-principal at read time
   rather than served as stored bytes.

We take (3). It means **the stored bytes of an entity page are never returned
verbatim by any API** — the API returns a projection. The `_id, title, type` header
is the only always-visible part, and even node *existence* is gated: a person node
whose every edge is invisible to you returns 404, not an empty page.

Hard rule, enforced in code: **no derived artifact may have a wider ACL than its
narrowest input.** Extraction can never widen an ACL — an LLM summary of a private
doc is as private as the doc.

### 6.4 Filtering vector search without wrecking recall

Post-filtering an HNSW result set is a correctness win and a recall disaster: if a
principal can see 2% of the corpus, top-100 ANN yields ~2 visible rows. Plan:

- **Coarse partition by sensitivity tier** — separate HNSW indexes per tier. A
  principal searches only the tiers they hold any grant in.
- **Within a tier, pre-filter with pgvector iterative index scan** (`hnsw.iterative_scan
  = relaxed_order`), which keeps scanning until it has enough rows passing the filter,
  instead of filtering a fixed candidate set.
- **Adaptive overfetch** with a measured recall floor. The retrieval evaluation
  harness (M4) tracks recall@k *per principal class*, so a permission-driven recall
  cliff shows up as a test failure, not a support ticket.
- **Defense in depth:** the ACL predicate is in the SQL, *and* the Python layer
  re-verifies every node ID against the principal's visible set before any content
  crosses the process boundary. Two independent checks, because a single bug in the
  first one is a headline.

Threat model we are explicitly designing against: the leak vectors are (a) a
retrieval path that forgets the filter, (b) a derived node that aggregates across ACLs,
(c) an agent that asserts its own identity, (d) the store itself being handed to
someone. §6.2, §6.3, §8.2, and this section address them in order.

---

## 7. Retrieval and synthesis

```
question + principal
  │
  ├─ 1. resolve principal → visible_refs, visible tiers          (§6)
  ├─ 2. candidate generation, ACL-filtered in SQL:
  │       a. pgvector cosine over chunks in visible tiers
  │       b. Postgres FTS (tsvector, BM25-ish ranking)
  │       └─ fuse with Reciprocal Rank Fusion (k=60)
  ├─ 3. graph expansion: from top-N seed nodes, traverse accepted
  │       edges ≤2 hops with per-predicate weights and a node budget;
  │       every expanded node re-checked against visible_refs
  ├─ 4. rerank (cross-encoder or LLM rerank) → context set with IDs
  ├─ 5. synthesize: model must emit claims tagged with node IDs
  └─ 6. CITATION VALIDATOR (blocking):
          - every cited ID ∈ context set          else → error
          - every cited ID visible to principal   else → error + alert
          - every non-trivial claim sentence has ≥1 citation
          - cited span, if given, exists in the node
        failure → the request fails. There is no uncited fallback answer.
```

Step 6 runs in the request path, not in tests. An answer with no citations is a bug
per the kickoff, so it is an exception, not a lower-quality response.

Hybrid is non-negotiable for this corpus: entity-name queries ("who owns vendor
renewals") are lexical-friendly and embeddings routinely miss exact identifiers,
ticket numbers, and tool names.

**Chunking** is structure-aware (split at heading boundaries, then pack to a token
bound with overlap) and deterministic. Chunks inherit `acl_ref` from their node.
Chunk boundaries are part of the index, not the markdown — rechunking is a reindex,
not a corpus rewrite.

---

## 8. Agents as first-class clients

### 8.1 MCP surface

| Tool | Semantics |
|---|---|
| `search(query, filters, limit)` | hybrid retrieval, ACL-filtered, returns node IDs + snippets |
| `traverse(node_id, predicates, depth, limit)` | typed expansion over accepted edges, ACL-filtered per hop |
| `read_node(node_id)` | ACL-projected node (§6.3), never raw stored bytes |
| `write_node(node_id, patch)` | writes a **proposal**, returns proposal ID |
| `propose_edge(subject, predicate, object, evidence)` | writes a proposal |

### 8.2 Identity

**The principal comes from the MCP session's authenticated credential. It is never a
tool parameter.** An agent must not be able to say "I am acting as the CFO". Agents
run with a delegated principal whose visible set is the *intersection* of the agent's
own grants and the invoking human's grants. Sessions are audit-logged with
`(principal, delegated_by, tool, node_ids_returned)` — node IDs, never content.

### 8.3 The write path

Agent (and low-confidence extraction) writes land in `store/_proposals/<id>.md` — real
markdown, diffable, reviewable in the same editor as everything else — plus a
`review_queue` row. Accepting a proposal is a normal store write followed by a
reindex. Rejection is retained, not deleted, because rejected proposals are the
training signal for tuning the gates in §11.

Proposals are ACL-inherited from the evidence they cite and cannot widen it (§6.3).

---

## 9. Ingestion and change management

### 9.1 Pipeline

`discover → fetch → normalize → extract (cached) → resolve entities → write store →
reindex`. Incremental by `(external_id, external_version, content_sha256)`; unchanged
artifacts skip normalization *and* extraction.

### 9.2 Writes are atomic and idempotent

Write to a temp file, fsync, rename. A partially-written store is never observable.
Re-running an ingest over an unchanged corpus produces a zero-line diff — that is the
test, and it runs in CI.

### 9.3 Upstream deletes and edits — **flagged**

*Edits.* Source version changes → the node is rewritten in place, same ID. Git is the
version log in dev; in prod, object-store versioning plus a `node_revisions` table.
Extraction re-runs (new content hash → new cache key). Edges whose evidence spans no
longer exist are demoted to `status: stale` and re-proposed rather than silently kept
or silently dropped — a citation pointing at text that no longer exists is worse than
no citation.

*Deletes.* Default is a **tombstone**, never a file removal:

```yaml
status: deleted
deleted_upstream_at: 2024-06-01T…
content_retained: false     # body replaced by a stub
```

Inbound edges are preserved but excluded from traversal; old answers' citations
resolve to "this source was deleted on <date>", which is a better answer than a
dangling ID.

**Three things I want a decision on, not a default:**

1. ~~**Retention on delete.**~~ **Decided (§14 Q3).** Purge the body on delete, retain
   the graph always, retain the body only under explicit per-connector opt-in.
   Sensitivity is *not* the axis — the original proposal (retain `internal`, purge
   `restricted`) tied an irreversible action to a field that describes who may read a
   document, not whether it still exists. The axis is the connector's delete signal.
   See §9.3.1.
2. ~~**Git makes true deletion hard.**~~ **Decided (§14 Q2).** No production store is
   git-backed. Object store with versioning, one bucket per tier, plus `node_revisions`
   in the same Postgres as the index. Git stays where it is — this repo, dev and CI —
   and never backs a tenant. Purging a body therefore means deleting *every* version of
   the object and the corresponding revision rows, not writing an empty one; a versioned
   bucket reproduces git's problem exactly if you let it. See §9.3.3.
3. ~~**Detecting deletes at all.**~~ **Answered by §9.3.2**, per connector, because the
   cost of enumeration differs per source and one global number would be either a lie
   or the slowest source's number applied to everything.

#### 9.3.1 What a disappearance means

Absence is not one signal, and the outcomes are not symmetric. `Disappearance` in
`connectors/base.py` is the vocabulary:

| Signal | Meaning | Node | Body |
|---|---|---|---|
| `TRASHED` | recoverable upstream for a window | tombstone | **retained** |
| `DELETED` | permanent upstream | tombstone | **purged** |
| `ACCESS_LOST` | the artifact exists; we can't see it | untouched | untouched |
| `UNKNOWN` | the source cannot say | untouched | untouched |

`UNKNOWN` is treated exactly as `ACCESS_LOST`. A connector that cannot distinguish a
delete from an unshare **must** say `UNKNOWN` rather than guess, because the two
mistakes cost different amounts: a delete detected late is correct but stale, while a
delete inferred wrongly purges a body that still exists upstream and nothing brings it
back. Every connector picks the reversible side.

This is why the seen-set diff alone never drives a purge. Google's changes feed is
explicit that `removed` means "removed from this list of changes, *for example* by
deletion or loss of access"; an enumeration diff inherits that ambiguity. Classifying
is a second, deliberate question asked of the source — `classify_departure` — not an
inference from the first.

#### 9.3.2 Deletion freshness SLA

Stated per connector and per signal, since the detection costs differ:

| Connector | Edits & trashes | Permanent deletion | Permission changes |
|---|---|---|---|
| Google Drive | 5 min (`changes.list`) | **24 h** (full `files.list` diff) | 5 min |
| Slack | 5 min (`conversations.history`) | not distinguishable — see below | 5 min |
| Local FS | per ingest run | per ingest run | n/a |

The incremental feeds are cheap and run every 5 minutes; full enumeration is O(corpus)
and runs daily. So a Drive file whose trash is emptied may keep its body for up to 24
hours after the purge. That window is the price of never purging on a guess, and it is
the right trade in that direction.

Slack has no row for permanent deletion on purpose: `conversations.history` on a
channel you have left returns the same error as one that was archived, so the
connector reports `UNKNOWN` and the content stays. Making that a delete would require
an audit-log integration, not a shorter interval.

Permission changes carry their own window (`base.py`): a principal removed upstream
can still retrieve until the next grant sync. Bounded and reported via `synced_at`,
never claimed to be zero.

#### 9.3.3 The production store — **resolved**

**Decision: object store with versioning, one bucket per sensitivity tier, plus a
`node_revisions` table in the same Postgres as the index. Git backs no tenant, at any
size.** The kickoff's third option — git for small tenants, object store for regulated
ones — is rejected along with plain git.

The obvious argument is §9.3.1: we purge bodies by default now, and git cannot delete.
An erasure request or a leaked credential needs `filter-repo` across every clone that
was ever taken, which is not an operation, it is a fire drill with no completion
criterion. But that argument alone would leave option (c) standing, so here is why it
does not.

**Git's remaining value is distributed authorship, and we already forbade distributed
authorship.** Strip out what git is not actually providing here:

- *Diffability* is a property of the format, not the storage. Canonical markdown with
  declared key order and sorted collections (§2.3, invariant 3) diffs identically
  whether it came from a bucket or a commit. `cb diff <id> --from <rev>` over
  `node_revisions` renders the same unified diff.
- *History* is better in a table than in a log. Git gives history per *commit*; we want
  it per *node*, and `git log --follow` is a rename heuristic that our own invariant 12
  defeats — an ID never moves, so a rename is a new file plus a tombstone, which git
  follows worse than a foreign key does.
- *Open it in an editor* is a property of checkout. `cb export` writes a real directory
  from a real revision; Obsidian does not know or care where the bytes came from. What
  you lose is that the directory is authoritative.

That last loss is the whole of it, and §15 and invariant 13 already took it. Writes are
server-authoritative, human edits are validated against fences *server-side* "because a
browser is not a trust boundary", and agents cannot write at all (invariant 9). A git
remote accepting pushes is a less controlled write path than the browser we already
refused to trust: it would make the store the permission boundary, which §6.2 exists to
deny. We would be paying git's costs for a capability the architecture rules out.

**And git is specifically corrosive to §6.2.** Physical tier roots only mean something
if content that moves between them stops existing in the looser one. A reclassification
from `internal` to `restricted` — the exact case `Repository._place` handles — leaves
the internal-era bytes in git history permanently, readable by anyone holding a clone at
the internal tier. Git would undo, in history, the boundary this design enforces in the
tree. That is not a corner case; it is the mechanism.

The option-(c) split also inverts its own risk. It hands the un-deletable store to small
tenants, who are the least equipped to run a history rewrite across their clones, and it
means every store invariant is implemented twice with the weaker implementation setting
the real guarantee — while the backend carrying 5% of deployments gets 5% of the
testing.

*What this costs, stated plainly.* The enterprise pitch is no longer "your knowledge
graph is a git repo you can push to." It is "your knowledge graph is canonical markdown
you can read, diff, export, and edit through a reviewed path." Read, diff and export
survive as first-class features and are cheap to build. Round-trip authoring by `git
push` does not survive; that traffic goes to the live editor and the proposal queue,
which is where invariants 9 and 13 already said the write path was. Anyone who wanted
git as *the* interface is being told no, and should be told so directly rather than
discovering it during a pilot.

*Consequences to build against.*

- A purge deletes all object versions plus the body column of every `node_revisions`
  row, and is idempotent and auditable. A soft-delete that writes an empty version is
  not a purge and must not be called one.
- `node_revisions` stores bodies, so it inherits the tier boundary: partitioned by tier
  or one table per tier, never one shared table under three separated buckets. Same
  requirement as the `_proposals/` and `_cache/` gaps in §6.2.
- Object versioning is the revision *store*; the table is the revision *index*. They can
  disagree after a partial failure, so reconciliation is a `cb doctor` check, not an
  assumption.
- Git keeps its current job unchanged: this repository, the committed synthetic corpus,
  the committed extraction cache, and `git diff --exit-code` over `store/` as the
  determinism gate. Nothing about dev changes.

---

## 10. Entity resolution — **flagged**

### 10.1 What I propose

Four layers, cheapest and most certain first. Nothing merges on string similarity
alone.

1. **Identity keys from source systems (auto-merge).** Slack user IDs, Google
   directory IDs, and corporate emails are authoritative. A Slack `U01ABC` and a Drive
   owner with the same verified email are the same person, full stop. Most of the real
   win is here, and it is not an ML problem — it is a connector-completeness problem.
2. **Curated aliases (auto-merge).** `people/sam-kaur.md` carries
   `aliases: [sam@co.com, "@samk", "Sam K."]`, human-owned, outside any generated
   fence. This is where accumulated human knowledge lands.
3. **Blocked candidate generation + scored match (propose, never auto-merge).**
   Blocking on normalized surname / initials / email local-part; features = name
   similarity, co-occurrence with already-resolved colleagues, team overlap, temporal
   overlap, channel overlap. Above threshold → a `same_as` **proposal** in the review
   queue with its evidence. Below → nothing.
4. **Unresolved mentions stay unresolved.** A mention we cannot resolve becomes
   `mentions_unresolved` with the surface string attached. It is visible, countable,
   and reviewable. It does not get guessed into an existing person.

**Merges are reversible.** A merge writes a `same_as` edge and a redirect tombstone;
it never destroys the losing node. Unmerging is a supported operation, because merge
errors are discovered months later, and an irreversible merge silently mixes two
people's records with no way back.

### 10.2 Where it will fail

- **Two real people, one short name.** Sam Kaur and Sam Kelly in the same Slack. Layer
  3 scores them as one; co-occurrence features actively make it worse if they work
  together. Mitigation: never auto-merge Person; require ≥1 identity-key overlap for
  high confidence.
- **Name changes.** Marriage, transliteration, preferred-name switches. Layer 1 saves
  us only if the directory ID is stable through the change, which it usually is and
  occasionally isn't.
- **Contractors and personal addresses.** `sam.kaur@gmail.com` in a forwarded thread
  with no directory record. We will under-merge, which is the correct failure
  direction but produces duplicate-looking people in the UI.
- **Role and shared accounts.** `support@`, `oncall`, `deploy-bot`. These are not
  people and will attract edges as if they were, distorting any "who owns X" answer.
  Proposal: an explicit `Account` type with `operated_by` edges, and a curated
  non-person list. This needs deliberate handling, not a threshold.
- **Bare first names in prose.** "Sam said we'd renew" in a doc with no other signal.
  Context-window co-reference is decent but not reliable enough to bet an ownership
  claim on. These stay unresolved.
- **Tools.** "Snowflake" the warehouse vs "Snowflake" the internal project codename.
  Same string, different type. Type-aware disambiguation helps; internal codenames
  that collide with vendor names are a permanent tax.

### 10.3 Processes are a different, harder problem

A Process has no identifier anywhere in any source system. The LLM names it, and it
names it differently every time: "vendor renewal", "supplier contract renewal",
"the renewal process". String matching over LLM-invented names is not entity
resolution; it is measuring the model's phrasing variance.

Proposal: **do not auto-merge Process or Decision nodes.** Instead, cluster candidate
process mentions by embedding + participant overlap + artifact overlap, and present
clusters to a human who names the process once. The named process becomes a curated
node; subsequent extraction matches *against the curated list* (a constrained
classification problem) rather than inventing free-text names. This is the single
biggest quality lever in the product and it is human-in-the-loop by design.

I'd rather ship M1 with ~20 hand-named processes in the synthetic corpus and a
matching-against-a-list extractor than with open-vocabulary process extraction that
produces 400 near-duplicate nodes and makes the graph look sophisticated while being
useless.

---

## 11. Where extraction needs a human — **flagged**

Gate policy is per-predicate, not a single global confidence threshold, because the
predicates differ enormously in both extractability and blast radius.

| Predicate | Reliability | Policy |
|---|---|---|
| `authored_by` | high — structural metadata, not inference | auto-accept |
| `mentions` (resolved entity + span) | high | auto-accept ≥0.85, else propose |
| `supersedes` | medium — needs temporal + version reasoning across docs | propose always |
| `depends_on` | low — prose about dependencies is ambiguous and aspirational | propose ≥0.7 |
| `handoff_to` | low — inferring org mechanics from chat | propose always |
| `owns` | **low, and highest blast radius** | propose always, ≥2 evidence spans from distinct docs |
| `Decision` extraction | low — proposals, options, and decisions read alike | propose always |
| Process naming/merge | lowest (§10.3) | human names it; extractor matches a curated list |
| `Person` `same_as` | varies | never auto-merge without an identity key |
| Anything that would widen an ACL | n/a | **hard block**, not a proposal |

The specific failure I most expect: **mention→ownership drift.** Sam is quoted about
the NetSuite renewal in four threads, so the model concludes Sam owns vendor renewals.
Sam was relaying a decision made by someone who never wrote it down. The system then
answers "Sam owns vendor renewals" with four confident citations, all of which
technically support the sentence they're attached to. This is worse than not knowing,
because it comes with evidence. Hence: `owns` is always human-gated, and the CLI
distinguishes "asserted by <person> on <date>" from "inferred from N mentions" in the
answer text.

Second expected failure: **the model resolves ambiguity by inventing plausible
structure.** Asked for handoffs, an LLM will produce handoffs. Mitigation is an
explicit "insufficient evidence" output that we accept and count, plus tracking the
proposal accept-rate per predicate as a quality metric — an accept-rate near 100%
means the gate is theater, near 10% means the extractor is wasting reviewer time.

---

## 12. Stack: agreements and pushback

**Agreed:** Python 3.12, uv, FastAPI, Postgres+pgvector, Pydantic as schema source of
truth, pytest with a synthetic corpus. Adding: `ruff`, `mypy --strict` on `schemas/`
and `acl/`, Typer for the CLI, Alembic for migrations.

**Pushback / amendments:**

1. **Postgres FTS, not just vectors.** "Hybrid" in the kickoff is vector + graph. It
   needs a lexical leg too: this corpus is full of exact identifiers (tool names,
   ticket IDs, people) that embeddings blur. Free with Postgres, so this is a
   no-brainer.
2. ~~**Object store for prod markdown loses git.**~~ **Resolved: (b).** Object store
   plus versioning plus a `node_revisions` table, one bucket per tier; git for dev and
   CI only, never for a tenant. (c) is rejected too — two production backends means the
   weaker one sets the real guarantee, and the weaker one here cannot hard-delete, which
   §9.3.1 now requires. Diffability was never git's to give: it comes from the canonical
   format, so `cb diff` and `cb export` keep it. What is actually lost is authoring by
   `git push`, which §15 and invariants 9 and 13 had already ruled out. Full reasoning
   and the consequences to build against are in §9.3.3.
3. **Don't generate SQL from Pydantic.** §5.
4. **Pin document converters exactly and version them in frontmatter.** §4. This is a
   real constraint on dependency updates and should be stated in CLAUDE.md, which it is.
5. **Commit the extraction cache.** §4. This is the load-bearing trick that makes the
   byte-identical acceptance criterion honest. It is unusual and I want it confirmed.
6. **`Account` as a first-class type** alongside Person, for bots and shared inboxes.
   §10.2.
7. **Sensitivity tiers as physical store roots**, not just a frontmatter field. §6.2.

---

## 13. Rejected alternatives, consolidated

| Decision | Chosen | Rejected | Why |
|---|---|---|---|
| Canonical store | Markdown + YAML | Postgres canonical, markdown export | Kickoff requirement, and the editor affordance is the product's differentiator |
| Node ID | `type/slug-hash6` | Opaque ULID | Readability requirement; pay the rename cost via redirects |
| Edge encoding | Frontmatter authoritative, body links lifted | Body wikilinks only | Wikilinks can't carry confidence/evidence/status |
| Entity page writes | Fenced generated regions | Regenerate whole file | Would destroy human annotation, killing co-authorship |
| ACL storage | `acl_ref` + grants table | Materialized principal list per node | Avoids corpus-wide rewrite on every membership change |
| Derived node ACL | Per-edge ACL, read-time projection | Union (leaks) / intersection (useless) | Only option that's both safe and useful |
| Vector store | pgvector in the same DB | Dedicated vector DB | Keeps ACL filter and rebuild in one transactional store |
| Extraction determinism | Committed content-addressed cache | Re-run + semantic assertions | Makes byte-identical re-ingestion a real, testable property |
| Process entities | Curated names, match-against-list | Open-vocabulary LLM naming | Otherwise the graph fills with near-duplicates |
| Agent writes | Proposals in `_proposals/` + queue | Direct writes with rollback | Rollback after an agent poisons the graph is not a real remedy |
| Retrieval | vector + FTS + graph, RRF | Vector-only | Exact-identifier queries are the common case here |

---

## 14. Open questions for your review

1. **Commit the extraction cache to the repo?** (§4) It makes the acceptance criterion
   honest but adds ~1 JSON per document to version control.
2. ~~**Prod store: git, S3+revisions, or tiered?**~~ (§9.3, §12.2) — **decided: object
   store with versioning, one bucket per tier, plus `node_revisions`. Git backs no
   tenant at any size.** Forced by Q3: purging bodies requires hard-delete, and git
   cannot. The tiered compromise is rejected separately — it would give the
   un-deletable backend to the tenants least able to rewrite history. "Open it in an
   editor" stays real as read, diff and export (`cb export`, `cb diff`); it stops being
   real as `git push`, which §15 and invariants 9 and 13 had already ruled out.
   Reasoning in §9.3.3, enforcement of the per-tier buckets in §6.2.1.
3. ~~**Retention policy on upstream delete**~~ (§9.3.1) — **decided: purge by default,
   with per-connector opt-in retention.** The graph is always retained; only the body
   is purged, so citations still resolve to a dated tombstone. Keyed on the connector's
   delete signal, never on sensitivity. Implemented in `SyncEngine._depart` and
   classified per source by `Connector.classify_departure`; the freshness windows that
   make "delete" a meaningful word are in §9.3.2.
4. **Is the ACL enforcement boundary at the API acceptable for the first enterprise
   conversation**, given the store itself is all-or-nothing? (§6.2) If not, per-tier
   encryption moves from M5 to M1 and changes the store design.
5. **Scope of M1 processes**: I want ~20 hand-named processes in the synthetic corpus
   and a constrained extractor, not open-vocabulary extraction. (§10.3) Agree?
6. **Who is the reviewer persona** for the review queue? If it's an ops team, the gates
   in §11 are right. If it's the executive asking the question, the volume is far too
   high and we need to auto-accept more and surface uncertainty in the answer instead.

---

## 15. Live collaboration — **demo-grade, deliberately**

Two people open the same node, both type, both see each other's cursors and text
land with no save button; a shared room lets a team sit inside one `ask` session
together. This section exists because that feature is the one place in the system
where we have knowingly shipped something that loses data, and a reader who does not
know that will mistake it for the real thing.

### 15.1 The merge rule

**Server-authoritative, last-write-wins.** The room holds the authoritative body and
a monotonic revision. A client sends `{type: "edit", base_revision, body}`; the
server *always* accepts, bumps the revision, and broadcasts the whole body to
everyone. Persistence is debounced — after ~800ms of quiet the room flushes through
`Repository.put`, which is what makes "no save button" true without a file write per
keystroke.

**What this costs.** Two people editing the same paragraph inside one round trip: the
later write replaces the *entire* body, and the earlier typist's sentence is gone with
no conflict, no marker, and no undo. Fast broadcast makes the window small and
presence makes collisions socially visible; neither makes them impossible. `clobbered`
is set on the outcome so the loss shows up in logs rather than silently, and
`tests/unit/test_collab.py::TestLastWriteWins::test_a_stale_write_still_wins_and_says_so`
asserts the data loss on purpose — turning this into a real merge should require
changing that test, not just adding code.

### 15.2 What a live edit may touch

Invariant 13 says machine writers touch only the interior of a generated fence. Live
editing is its mirror image: a **human** writer may touch only the text *outside*
every fence. `collab/guard.py` compares the generated regions before and after every
edit — name, interior, and recorded hash — and refuses the write if any of them moved.

This runs on the server. A browser is not a trust boundary, and a client that strips a
fence or rewrites a generated interior gets rejected and resynced, not persisted.

### 15.3 Durability differs by node type — know which you are editing

| Node type | A live edit… | Why |
|---|---|---|
| Entity page (Person, Team, Tool, Process) | **survives ingest forever** | `_write_entities` skips nodes that already exist |
| Document node | **is replaced at the next ingest of its source** | a Document mirrors an upstream artifact; invariant 1 says the source wins for sourced content |

This is by design, not an oversight, and both halves are pinned in
`tests/acceptance/test_m1.py::TestLiveEditDurability`. But it is a sharp edge: a user
who annotates a Slack thread's Document node will lose the annotation on the next
sync. Annotation belongs on entity pages. If we want durable per-document human text,
it needs its own fenced human region — not a change to the live editor.

### 15.4 Identity

A browser cannot set `X-Principal` on a WebSocket, so the header stand-in does not
carry over. The principal travels in the `Sec-WebSocket-Protocol` subprotocol
(`cb.principal.<id>`), fixed at connect time and impossible to restate per message —
which is what invariant 8 actually requires. A query parameter would have been a
parameter the caller can vary, which is the thing the invariant forbids. Same demo
stand-in for a session cookie as `X-Principal`; the shape is what matters.

ACL is checked on connect and the socket closes with `4404` for both "no such node"
and "not visible to you" — distinguishing them would confirm a node's existence to
someone who cannot read it (§6.3).

### 15.5 The shared ask room

One question, one broadcast — but **each participant's answer is computed under their
own grants**, never copied from the asker. The room fans out per principal through the
same `answer_for` helper the REST route uses, so the citation validator (invariant 11)
runs on every answer on both surfaces. Broadcasting one principal's answer to a room
is the obvious way to build this and is a leak wearing a collaboration costume.

### 15.6 Rejected alternatives

| Decision | Chosen | Rejected | Why |
|---|---|---|---|
| Merge model | Server LWW, whole body | CRDT (Yjs / Automerge) | A CRDT replaces the whole-file write model that the byte-identical acceptance gate and the fence hashes both depend on. That is an M5-scale change to §2, not a library swap |
| Merge model | Server LWW | Operational transform | Same objection, plus OT needs a server that understands document structure; ours understands bytes |
| Persistence | Debounced flush | Write per keystroke | 232-node index, atomic rename per character |
| Persistence | Debounced flush | Explicit save button | The product claim is "no save button"; a WAL is the honest fix for the lost-window problem, not a button |
| Room state | In-process registry | Redis/Postgres backplane | Correct for multi-worker, unnecessary for one. **This pins us to a single uvicorn worker** — two workers would each hold a different authoritative body for the same node |
| Presence colour | Server sends a palette *name* | Server sends hex | DESIGN_SYSTEM §2 bans raw hex in the UI; the name→class map lives in the client |

### 15.7 What production would need

Not a longer version of this — a different design. A CRDT or OT layer for real
concurrent editing; a write-ahead log so the debounce window is recoverable; a shared
backplane so more than one worker can serve a room; per-document human regions if
Document nodes are to be annotatable; and an audit trail of who changed which bytes,
which today exists only as the git history of the store.
