# company_brain — Architecture

Status: **proposal, awaiting review**. Nothing here is implemented.

This document decides the things that are expensive to change later: the on-disk
format, the identity/ID scheme, the permission model, and the boundary between
deterministic and model-generated content. It records rejected alternatives
alongside the choices, because in most cases the rejected option was reasonable
and we may want to revisit it.

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
  documents/
    slack/2024/03/eng-standup-2024-03-14-a91f3c.md
    gdrive/vendor-renewal-policy-4d20be.md
    email/re-netsuite-renewal-thread-77c0a1.md
  people/sam-kaur.md
  teams/support.md
  tools/netsuite.md
  processes/vendor-renewal.md
  decisions/2024-03-adopt-netsuite-4e91.md
  _proposals/                      # agent + low-confidence writes, not yet graph
  _cache/extraction/<key>.json     # committed; see §4
  _tombstones/                     # deleted upstream, retained as redirects
```

Directory structure is for humans and for `git log --follow`. It is not load-bearing:
the index is built by walking `store/**/*.md`, not by parsing paths.

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

### 4.1 Evidence spans: an unresolved conflict — **flagged**

§11 requires every LLM-derived edge to carry an evidence span. Two mechanisms
could supply one, and they are mutually exclusive within a single API call:

1. **Structured outputs** (`output_config.format`, or `client.messages.parse()`
   against our Pydantic models) — schema-validated extraction with no parsing
   layer, but any span the model reports is self-asserted and routinely off by a
   few characters.
2. **Native citations** (`citations: {enabled: true}` on a document block) —
   returns `cited_text` plus exact `start_char_index` / `end_char_index` computed
   by the API rather than guessed by the model. Far more trustworthy.

**Citations return a 400 when combined with `output_config.format`.** So we can't
have both in one call. Options: a two-pass extraction (structured pass for
entities and predicates, citations pass to locate evidence), or strict tool use
(`strict: true`) in place of `output_config.format`, if citations coexist with
tool use. M1 tests both against the synthetic corpus and takes whichever produces
spans that actually resolve.

Flagged because it shapes the `extract/` module, and because self-reported spans
would quietly undermine the §11 gates — a reviewer checking evidence that points
at the wrong text is worse than having no gate at all.

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

- The store is classified at the **maximum** sensitivity of anything in it.
- Dev machines get the synthetic corpus, never a production store.
- For prod, sensitivity tiers are **physically separated** into distinct store roots
  (`store-public/`, `store-internal/`, `store-restricted/`) with separate object-store
  buckets and IAM. A tier is the coarse-grained boundary; `acl_ref` is the
  fine-grained one within a tier. This also gives us the ANN partitioning in §6.4.
- Connectors must be able to refuse: a `restricted` source cannot be ingested into a
  store root that is not `restricted`. Enforced in the writer, not by convention.

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

1. **Retention on delete.** Do we keep the content of a deleted doc? Keeping it is
   great for "why did we decide X" and legally dangerous. My proposal: retain for
   `internal`, purge body for `restricted`, tier-configurable.
2. **Git makes true deletion hard.** A GDPR erasure request or a leaked-credential
   commit cannot be satisfied by a new commit; it needs history rewriting across every
   clone. Proposal: for regulated tenants, the prod store is object-store-with-versioning
   plus a revisions table (both support real hard-delete), and git-backed stores are a
   dev-and-small-tenant affordance only. This partly contradicts the "open the repo in
   an editor" pitch for enterprise and is worth an explicit call.
3. **Detecting deletes at all.** Most connectors don't push delete events reliably;
   detection means periodic full enumeration and diffing. That is a real cost at scale
   and needs a stated SLA ("deletions reflected within 24h") rather than an implied
   one.

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
2. **Object store for prod markdown loses git.** The kickoff leans on diffability, and
   S3 is not a version-control system. Options: (a) git-backed bare repo, versioning
   for free, poor at 10M files; (b) S3 + object versioning + a `node_revisions` table,
   scales, and we rebuild "diff" ourselves; (c) both, tier-dependent. I lean (c) with
   git only for dev and small tenants — see §9.3(2). **Needs your call.**
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
2. **Prod store: git, S3+revisions, or tiered?** (§9.3, §12.2) This determines whether
   "open it in an editor" is a real enterprise story or a dev-only one.
3. **Retention policy on upstream delete** (§9.3.1) — retain by default, or purge by
   default with opt-in retention?
4. **Is the ACL enforcement boundary at the API acceptable for the first enterprise
   conversation**, given the store itself is all-or-nothing? (§6.2) If not, per-tier
   encryption moves from M5 to M1 and changes the store design.
5. **Scope of M1 processes**: I want ~20 hand-named processes in the synthetic corpus
   and a constrained extractor, not open-vocabulary extraction. (§10.3) Agree?
6. **Who is the reviewer persona** for the review queue? If it's an ops team, the gates
   in §11 are right. If it's the executive asking the question, the volume is far too
   high and we need to auto-accept more and surface uncertainty in the answer instead.
