# company_brain — Roadmap

Five milestones, each independently demoable to someone who has not seen the previous
one. "Demoable" means: a scripted 5-minute walkthrough against committed fixtures, with
a named audience and a claim it proves.

Permissions are not a milestone. Per the kickoff they are load-bearing from day one, so
the ACL schema and enforced filtering ship inside M1 with synthetic principals; M2 makes
them real by wiring live source-system grants.

---

## M1 — The vertical slice

**Claim:** a directory of mixed files becomes a queryable, cited knowledge graph, and
re-ingesting it changes nothing.

**Audience:** you.

### Scope

- **Corpus.** ~200 synthetic files committed to `corpus/synthetic/`: `.md`, `.pdf`,
  `.docx`, `.eml`, Slack export JSON. Modeled on a plausible 60-person company —
  Support, Engineering, Finance, a handful of tools, ~20 hand-named processes including
  vendor renewals, and at least three deliberately messy cases (a person with four name
  forms, a shared `support@` inbox, two tools with colliding names).
- **10 seeded questions** with expected answers *and* expected citation node IDs, in
  `corpus/synthetic/goldens.yaml`.
- **Normalizers** for the five formats. Pure, version-stamped, deterministic.
- **Store**: canonical YAML emit, atomic writes, generated-region fences, ID scheme,
  tombstone stubs.
- **Extraction**: 6 entity types, 6 predicates, evidence spans, per-predicate gate
  policy (ARCHITECTURE §11), committed content-addressed cache.
- **Entity resolution layers 1–2 only**: identity keys and curated aliases. Layer 3
  (scored candidates) lands in M3. Unresolved mentions stay unresolved and are counted.
- **Index**: full schema, `rebuild --from-scratch`, `cb doctor`.
- **ACL**: `acl_ref` on nodes and chunks, `acl_grants`, synthetic principals
  (`ceo`, `support-lead`, `eng-ic`, `contractor`), filtering enforced in SQL and
  re-verified in Python.
- **Retrieval**: pgvector + FTS + RRF, 2-hop typed traversal, citation validator.
- **MCP server**: `search`, `traverse`, `read_node` (read-only this milestone).
- **CLI**: `ingest`, `index rebuild`, `doctor`, `ask`, `mcp serve`.

### Acceptance

1. `cb ask` answers all 10 seeded questions with correct citations.
2. Full re-ingestion produces a **byte-identical** markdown tree (`git diff --exit-code`),
   with a frozen extraction cache.
3. `index rebuild --from-scratch` reproduces an index identical to the incremental one.
4. **Permission test**: the same question asked as `ceo` and as `contractor` returns
   different answers, and no `contractor` answer cites a node they cannot read. A
   deliberately planted private comp discussion is never retrievable by non-`ceo`
   principals — asserted at the retrieval, MCP, and CLI layers independently.
5. `cb doctor` is clean.

### Demo

Ingest the corpus cold → show the git diff (a full tree) → re-ingest → show the empty
diff → `cb ask "who owns vendor renewals?"` → open the cited markdown files in an
editor → ask the same question as `contractor` and get a narrower, still-cited answer.

### Explicitly out

Live connectors, agent writes, incremental sync, deletion handling, scored entity
resolution, any UI.

---

## M2 — Real sources, real permissions, real change

**Claim:** it stays correct when the world moves — documents get edited, deleted, and
re-shared, and permissions come from the actual source systems.

**Audience:** a friendly design partner willing to point us at a real Slack workspace
and Drive folder.

### Scope

- **Connectors**: Slack (history + membership), Google Drive (files + sharing scopes),
  Gmail. Each derives an `acl_ref` and syncs `acl_grants` on a schedule.
- **Incremental sync** with cursors; unchanged artifacts skip normalize and extract.
- **Change handling** (ARCHITECTURE §9.3): edits rewrite in place with a revision log;
  deletes produce tombstones; edges with vanished evidence spans go `stale` and
  re-propose.
- **Delete detection** via periodic enumeration + diff, with a stated freshness SLA.
- **Permission-change propagation**: someone leaves a channel → their answers narrow
  within one grant-sync cycle, with no corpus rewrite.
- **Sensitivity tiers as physical store roots**; a connector cannot write a `restricted`
  source into a non-`restricted` root.
- Resolve open questions 2 and 3 from ARCHITECTURE §14 (prod store backend, retention
  on delete) — both block this milestone's design.

### Acceptance

- Sync a real workspace; `cb doctor` clean after three consecutive incremental syncs.
- Edit a Drive doc upstream → next sync produces a minimal, reviewable diff, not a
  rewrite of the file.
- Delete a doc upstream → it disappears from answers; a prior answer's citation resolves
  to a tombstone with a date.
- Remove a principal from a private channel → within one sync, their `ask` no longer
  retrieves that channel, verified at all three layers.
- Re-ingesting an unchanged workspace is still a zero-line diff.

### Demo

Side-by-side: the app, and Slack/Drive. Change a permission live, run the sync, ask the
question again, and watch the answer narrow.

---

## M3 — Humans and agents co-author the graph

**Claim:** the graph gets better through use, and agents can contribute without being
able to corrupt it.

**Audience:** a design partner's ops person — the reviewer persona.

### Scope

- **Entity resolution layer 3**: blocked candidate generation, scored matching,
  `same_as` proposals with evidence. Reversible merges; unmerge is a tested path.
- **`Account` type** for bots and shared inboxes, with `operated_by`.
- **Review queue, end to end**: `cb review list/show/accept/reject/bulk`, plus a minimal
  web review UI (a diff view over proposals — this is where a UI first pays for itself).
- **Agent write path**: MCP `write_node` and `propose_edge` live, writing to
  `store/_proposals/`, ACL-inherited and unable to widen.
- **MCP session auth** with delegated principals (agent grants ∩ human grants) and a
  full audit log.
- **Human edits round-trip**: edit a file in Obsidian → next ingest lifts body wikilinks
  into `relations` with `provenance: human` → generated fences respect the edit → the
  human's text survives forever.
- **Gate telemetry**: per-predicate proposal volume and accept-rate, so we can tell
  whether a gate is theater or a bottleneck.

### Acceptance

- An agent attempting a direct graph write is rejected; the attempt is audited.
- An agent attempting to widen an ACL is blocked, not queued.
- A merge, then an unmerge, then a re-ingest returns the store to a byte-identical state.
- A human annotation on an entity page survives 10 ingest cycles.
- Reviewer processes 50 queued proposals in under 15 minutes without opening a terminal.

### Demo

Point a Claude agent at the MCP server; it researches a question, proposes three edges;
the reviewer accepts two and rejects one; ask the question again and the answer improved
— with the reviewer's name on the provenance.

---

## M4 — The company as a system

**Claim:** the original pitch. "Where are handoffs between Support and Engineering
breaking down?" gets a sourced answer in minutes.

**Audience:** an executive buyer.

### Scope

- **Process modeling**: curated process nodes with steps, owners, inputs/outputs, and
  the artifacts and teams touching each step. Extraction matches against the curated
  list (ARCHITECTURE §10.3), it does not invent names.
- **Handoff analysis**: `handoff_to` edges enriched with observed latency, volume, and
  rework signals mined from the artifacts (thread reopenings, ticket bounces, repeated
  escalations).
- **Systemic queries**: single-owner-no-backup, ownerless processes, cross-team
  round-trips, tools with no owning team, processes whose only documentation is a Slack
  thread.
- **Evidence-grade synthesis**: answers separate *asserted* facts ("Sam is named owner
  in doc X") from *inferred* patterns ("14 of 20 escalations in Q1 bounced back from
  Engineering"), each cited, each with a confidence and a "how I know this" expansion.
- **Evaluation harness**: 100+ golden questions across question classes (factual,
  ownership, temporal, systemic, unanswerable), with **recall@k tracked per principal
  class** so a permission-driven recall cliff fails a test. Regression-gated in CI.
- An explicit, tested **"insufficient evidence"** answer, and a metric for how often we
  say it.

### Acceptance

- Answers the handoff question against a real design-partner corpus, and the design
  partner agrees with the finding.
- Evaluation suite green; no regression versus M3 on the M1 goldens.
- Every systemic claim expands to the underlying node IDs in one click/keystroke.
- On a question the corpus genuinely cannot answer, the system says so rather than
  confabulating.

### Demo

The exec asks their own question, unrehearsed. Answer in under two minutes. Drill from
the claim to the Slack thread it came from.

---

## M5 — Production

**Claim:** it can be sold, deployed, and operated for someone else's data.

**Audience:** a security reviewer and an on-call engineer.

### Scope

- **Multi-tenant isolation**: per-tenant stores, indexes, and credentials. Tenant ID in
  every query path, enforced at the connection level, not in application filters.
- **Object-store backend** for the markdown store (per the M2 decision), with the
  revision log and hard-delete/purge paths — GDPR erasure and secret-leak remediation
  are tested operations.
- **Encryption at rest per sensitivity tier**, if ARCHITECTURE §14.4 lands that way.
- **Scale**: incremental reindex, parallel ingest, ANN tuning with measured recall
  floors, ingestion backpressure. Target: 1M documents, p95 `ask` under 8s.
- **Observability**: ingest lag, cache hit rate, drift alerts from `doctor`, per-tenant
  cost, retrieval quality dashboards, an audit log that answers "who saw what, when".
- **Cost controls**: extraction budget caps per tenant, model tiering (cheap extract,
  expensive synthesize), cache hit rate as a tracked SLO.
- **Security review**: threat model in ARCHITECTURE §6.4 verified by someone who did not
  write it; adversarial tests for each of the four leak vectors.
- **Ops runbooks**: rebuild the index, recover from a bad prompt-version rollout, purge a
  document, rotate connector credentials.

### Acceptance

- Two tenants on one deployment; a cross-tenant read fails at the database, and the test
  proving it is in CI.
- 1M-document synthetic load meets latency and recall targets.
- Full index rebuild from object storage inside the stated RTO.
- Hard-delete of one document removes it from the store, all revisions, the index, the
  embeddings, and the extraction cache — verified by a test that greps for the content.
- External security review passes.

### Demo

An intentionally hostile walkthrough: try to make it leak, try to make it lie, kill the
database and rebuild it from the store.

---

## Sequencing notes

- **M1 is the only committed milestone.** M2–M5 are directionally right and will move.
- **The M1→M2 boundary is the risky one.** Everything in M1 runs against a corpus we
  authored, which means we have unconsciously made it tractable. Expect real Slack to
  break normalization determinism and real Drive to break the ACL model in some way this
  document did not anticipate. Budget for it.
- **The UI question resurfaces in M3.** Until then, the CLI plus an editor is a genuinely
  good interface for the audiences above and lets us avoid committing to a product
  surface too early. When it does land it follows [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)
  — the M3 review UI is the first piece of the real product surface, not a throwaway
  admin panel. Whether a ⌘K ask-with-citations surface should be pulled forward into
  M1's demo is open (DESIGN_SYSTEM §8); I still recommend CLI-first, since M1's risk is
  determinism and ACL correctness and a UI proves neither.
- **Four ARCHITECTURE §14 questions block work**: the extraction-cache decision blocks
  M1; the prod-store and retention decisions block M2's design; the reviewer-persona
  question determines whether M3's gates are correctly calibrated.
