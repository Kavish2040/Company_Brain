# CLAUDE.md — company_brain

Conventions and invariants for anyone (human or agent) working in this repo.
Design rationale lives in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); UI design
rules live in [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md); this file is the
operational contract. Read §Invariants before writing code.

## What this is

Ingests company artifacts (docs, PDFs, email, Slack, spreadsheets) into a markdown
knowledge graph that humans and agents both read and write, indexes it for query speed,
and answers executive questions with citations to specific node IDs.

**Markdown is the database. The index is a rebuildable cache.**

**Status: M1 is complete; M2's hard half is done in simulation.** Ingest → retrieve →
cited answer works, ACLs are enforced at three layers, and the sync engine handles edits,
deletions, orphaned evidence, and grant revocation against a mutable simulated Slack. Real
providers are wired (Claude extraction and synthesis, OpenAI embeddings); the offline path
remains a first-class fallback and is what CI runs. Still missing: the Postgres index, and
connectors to source systems that actually exist. §Current state has the detail.

## Stack

Rows marked ⏳ are decided but **not built** — do not assume they exist when reading code.

| Concern | Choice |
|---|---|
| Language | Python 3.12 |
| Packaging / env | uv (`uv sync --all-groups`, `uv run`) |
| CLI | Typer, entry point `company_brain` (alias `cb`) |
| Schemas | Pydantic v2 — single source of truth for nodes/edges/frontmatter |
| Store backend | `StoreBackend` protocol: local FS (dev), in-memory (tests), Supabase Storage |
| Extraction | `claude-sonnet-5` — strict tool + citations in one call (ARCHITECTURE §4.1); falls back to a deterministic roster matcher with no key |
| Synthesis | `claude-opus-5`, with an explicit INSUFFICIENT_EVIDENCE path |
| Embeddings | OpenAI `text-embedding-3-large` at **`dimensions=1536`** — pgvector's HNSW index caps at 2000 dims for `vector`, so native 3072 can't be indexed without `halfvec` |
| Index | `MemoryIndex` — BM25 lexical + cosine, rebuilt from markdown per process |
| API | FastAPI in `api/app.py`; principal arrives in `X-Principal`, never a request body |
| Frontend | `web/` — Vite + React 19 + TS strict, Tailwind v4, `lucide-react`, oxlint. Built to docs/DESIGN_SYSTEM.md |
| Agent surface | MCP server, stdio transport |
| Tests | pytest + a deterministically generated synthetic corpus |
| Lint / types | ruff, `mypy --strict` on `schemas/`, `acl/`, `store/` |
| ⏳ Index (real) | **Supabase** Postgres + pgvector |
| ⏳ Local stack | **`supabase start`** (Docker: Postgres, Storage, Auth, Studio) |
| ⏳ Migrations | **Supabase CLI, plain SQL in `supabase/migrations/`** — hand-written, **not** generated from Pydantic, and **not** Alembic (two migration tools on one database is a footgun) |
| ⏳ DB driver | `psycopg[binary,pool]` v3 direct — not `supabase-py`, which can't express the vector + FTS + RRF queries |
| ⏳ Lexical search | Postgres FTS (`tsvector`) — no Elasticsearch |
| ⏳ Real connectors | Slack, Google Drive, Gmail. Only `simulated-slack` exists |

### Online, offline, and why it matters for your wallet

`choose_providers()` in `app.py` is the only place that decides. It prints its reason on
every `cb ingest`, so a run is never silently degraded.

- **Both keys or neither.** Claude extraction scored against hash-based embeddings is a
  hybrid nobody asked for, and "offline, because `OPENAI_API_KEY` is unset" is far easier
  to diagnose than unexplained retrieval quality.
- **`.env` auto-loads** from `company_brain/__init__.py` — not from `app.py`, so a script
  importing a single module still gets credentials. `override=False`, so an exported
  variable beats the file.
- **`COMPANY_BRAIN_OFFLINE=1` forces offline.** This is the switch that keeps CI free and
  deterministic.

⚠️ **Run the test suite offline.** With a populated `.env`, plain `uv run pytest` picks
the online providers and the acceptance fixture re-extracts all 201 corpus documents
through Claude on every run — measured at 12+ minutes and real spend, versus **24 seconds**
with `COMPANY_BRAIN_OFFLINE=1`. Its store is a temp directory, so the extraction cache is
thrown away each time and nothing amortizes. The same applies to any `cb` command: online,
`cb index` and `cb ask` embed the whole corpus per process.

## Layout

```
src/company_brain/
  __init__.py  loads .env for every entry point (see above)
  app.py       COMPOSITION ROOT. Providers, grants, principals, and store roots are
               chosen here and nowhere else. Nothing else constructs an App.
  schemas/     Pydantic models. Nothing imports downward. Everything imports this.
               ids.py (slugs, IDs, paths) · nodes.py (Node, Frontmatter, NodeType)
               edges.py (Predicate, Edge, GATES, decide_status) · acl.py (AclRef,
               Principal, Sensitivity, narrowest)
  store/       canonical markdown store.
               backend.py (StoreBackend protocol + local/memory/Supabase, atomic writes)
               repository.py (get/put/walk, tombstones, redirects, ACL-widening guard)
               fences.py (generated regions, tamper detection) · serialize.py (canonical YAML)
  normalize/   bytes -> markdown + structural frontmatter. PURE. No LLM, no I/O beyond
               the input bytes. base.py (Normalizer, Registry) · formats.py (md/pdf/docx/eml/slack)
  extract/     base.py (Extractor protocol, CachedExtractor, content-addressed cache)
               claude.py (claude-sonnet-5, API-computed evidence spans)
               rules.py (the deterministic offline extractor)
  connectors/  base.py (Connector protocol: content, existence, permissions + SyncState)
               sync.py (SyncEngine: edits, deletes, stale evidence, grant mirroring)
               simulated.py (a mutable in-memory Slack — a working connector, not a mock)
               local_fs.py (directory ingest; the M1 path)
  corpus/      generate.py — deterministic generator for the synthetic corpus
  index/       base.py (chunking, Embedder, Index protocol) · memory.py (the index in use)
               openai_embed.py (text-embedding-3-large @1536)
  acl/         grants.py — GrantTable, AccessFilter, the single audited elevate()
  retrieve/    hybrid.py — candidate generation, RRF, weighted graph expansion
  synthesize/  answer.py (Synthesizer protocol, extractive fallback, citation validator)
               claude.py (claude-opus-5; output still goes through the same validator)
  review/      queue.py — proposal queue: list, accept, reject, per-predicate accept rate
  mcp/         server.py (Session, McpTools) · stdio.py (transport)
  cli/         main.py — Typer commands
  api/         app.py — FastAPI, ACL-projected responses, X-Principal header
  resolve/     entity resolution: identity keys, aliases, candidate scoring — empty; M3
corpus/synthetic/    committed corpus (201 files), regenerable byte-identically
store/               generated markdown tree — COMMITTED, not gitignored: re-ingestion is
                     verified with `git diff --exit-code` over this tree
  store/_cache/      committed extraction cache — what makes `--frozen` CI possible
  store/_proposals/  agent writes land here, never in the graph
  store/_sync/       connector cursors and last-seen id sets (NOT derived — see invariant 2)
supabase/            config.toml + migrations/*.sql (not created yet)
web/                 src/App.tsx (shell + principal switcher) · views/ (Ask, Browse,
                     Review, NodeDrawer) · components/ui/primitives.tsx · lib/api.ts
scripts/run.sh       dev entry point: setup, check, test, all, demo, api, web, mcp
tests/               unit/ · integration/ (empty until the database lands) · acceptance/
docs/
```

Dependency direction is strictly downward: `schemas` ← everything; `store` never imports
`index`; `retrieve` never imports `store` (it reads through `index` and `store`'s public
read API). Circular imports are a design smell here, not a nuisance. `app.py` is the one
exception by construction — it sits above everything; CLI, MCP, and the API import from it,
never the reverse.

Heavy imports (`corpus.generate`, `connectors`, `review`, both Claude modules) are deferred
into function bodies so `cb --help` stays fast and an offline run never imports `anthropic`.
Keep it that way.

## Commands

```bash
./scripts/run.sh setup                   # uv sync --all-groups: deps + dev + pinned converters
./scripts/run.sh all                     # ruff + format + mypy, then pytest
./scripts/run.sh demo                    # corpus -> ingest -> index -> determinism -> ask x2
./scripts/run.sh api & ./scripts/run.sh web   # FastAPI on :8000, Vite on :5173
```

`uv sync` alone does **not** install the `converters` group, and PDF/docx/email
normalization fails without it. Use `--all-groups`.

```bash
uv run cb corpus [--force]               # regenerate corpus/synthetic (deterministic)
uv run cb ingest corpus/synthetic        # normalize + extract + write store
uv run cb ingest corpus/synthetic --frozen     # fail on extraction cache miss (CI mode)
uv run cb sync [--connector simulated-slack] [--no-deletes]   # incremental sync
uv run cb index                          # rebuild the index and report its stats
uv run cb doctor                         # store/index drift check; non-zero on drift
uv run cb ask "who owns vendor renewals?" [--principal ceo|support-lead|eng-ic|contractor]
uv run cb principals                     # what each synthetic principal can see
uv run cb review list [--predicate owns] | uv run cb review stats
uv run cb review accept '<node_id>|<predicate>|<object>'
uv run cb mcp                            # print the tool contract as JSON
uv run cb mcp --serve --as ceo           # stdio MCP server; identity bound at startup

COMPANY_BRAIN_OFFLINE=1 uv run pytest    # the whole suite, free and deterministic
uv run pytest -m acceptance              # the M1 gate
uv run pytest -m llm                     # live model calls; not run in CI

supabase start                           # ⏳ local Postgres + pgvector + Storage
supabase db reset                        # ⏳ apply migrations from scratch
```

Every `cb` command takes `--store PATH` (default `store/`).

Things that surprise people:

- **`cb index` is a report, not a prerequisite.** The index lives in memory and is rebuilt
  from markdown on every process start, so `cb ask` indexes before it answers. There is no
  incremental or persistent index yet. That is invariant 2 taken literally, and it stops
  being free somewhere north of this corpus size — online, it also re-embeds every time.
- **`cb ask` exit codes are load-bearing.** `2` = citation leak blocked, `3` = refused as
  uncited, `1` = ordinary failure. Never soften either into a printed warning.
- **`./scripts/run.sh demo` starts with `rm -rf store`.** An interrupted demo leaves a
  half-ingested tree — documents but no entity nodes, and `cb doctor` reporting hundreds of
  dangling edges. Re-run the ingest; the state is not corruption, just incompleteness.
- **Only `acceptance`, `integration`, and `llm` are real markers.** Unit tests carry no
  marker, so `pytest -m unit` selects nothing. Select them by path: `pytest tests/unit`.

Test markers: `integration` (needs Postgres; no tests yet), `llm` (needs an API key;
excluded from CI), `acceptance`. `pytest` runs everything except `llm`. CI runs the suite
with `COMPANY_BRAIN_OFFLINE=1` and a frozen extraction cache, and never calls a model.

## Invariants

Breaking any of these is a revert, not a review comment. The pointer after each says where
it is enforced today — if you change that code, you are changing the contract.

1. **Markdown wins.** No code path writes to the index without the corresponding markdown
   write having succeeded first. There is no index-only state.
   → `connectors/` writes through `Repository`; `App.load_index` reads only `repo.walk()`.
2. **The index is disposable.** A from-scratch rebuild must fully reproduce the index from
   `store/` alone. Anything that can't be rebuilt from markdown doesn't belong in it.
   By-design exceptions, all workflow state rather than derived data: `principals`,
   `acl_grants`, `review_queue`, `ingest_runs`, and **connector sync state**
   (`store/_sync/` — cursors and last-seen id sets, moving to the `sources` table).
   → `App.load_index`; `tests/acceptance/test_m1.py::TestIndexRebuild`.
3. **Normalization is pure.** `normalize/` is a function of `(source bytes, normalizer
   version, config)` and nothing else. No wall-clock, no `uuid4`, no randomness, no
   locale-dependent formatting, no unordered iteration in output paths. Same input →
   byte-identical output, forever.
   → `TestDeterminism`, including a concurrency case. The corpus generator holds the same
   bar: fixed `SEED`, fixed `EPOCH`, zeroed zip mtimes in `normalize_zip`.
4. **No wall-clock timestamps in canonical files.** All timestamps come from the source
   artifact. Ingestion time belongs in `ingest_runs`; sync time belongs in `store/_sync/`.
5. **Every retrieval function takes an explicit `Principal`.** No default argument, no
   `None`, no `Optional`. Elevated access exists only via one audited helper in `acl/` and
   is never used in a request path.
   → `HybridRetriever(index, access)`; `AccessFilter`; `acl.grants.elevate()`.
6. **Never widen an ACL.** A derived node, summary, embedding, or proposal inherits the
   narrowest ACL of its inputs. Extraction cannot broaden visibility. Enforced in the
   writer, not by convention.
   → `Repository.put(input_tiers=…)` raises `AclWideningError`; `schemas.acl.narrowest`.
7. **The store is not a permission boundary.** Enforcement is at API/MCP/CLI. Treat the
   whole store as classified at its most sensitive content. Never put production content on
   a dev machine.
8. **Principals are never a tool/API parameter.** Identity comes from the session. An
   agent's effective visibility is the intersection of its own grants and the invoking
   human's.
   → `mcp.server.Session(agent_id, delegated_by)` bound by `cb mcp --as` at startup; the
   API's `X-Principal` header resolved once in `get_access`, never read from a body;
   `test_agent_visibility_is_intersected_with_the_human`.
9. **Agents never write to the graph.** `write_node` and `propose_edge` create entries in
   `store/_proposals/` plus a `review_queue` row. Full stop.
   → `McpTools.write_node` returns `state: pending_review`;
   `test_write_node_produces_a_proposal_not_a_mutation`.
10. **Every edge carries `provenance`, `confidence`, `evidence`, and `status`.** Only
    `status: accepted` edges are traversed at query time.
    → `schemas/edges.py`; `_llm_edges_cite` rejects an uncited LLM edge at construction;
    `GATES` / `decide_status` implement the ARCHITECTURE §11 policy table.
11. **Answers must cite.** The citation validator runs in the request path, including on
    Claude output. Uncited or unresolvable-citation output is an error, never a degraded
    answer.
    → `synthesize.answer.validate` raises `UncitedAnswerError` / `CitationLeakError`;
    the API returns a `refused` field and empty text rather than prose; `TestCitationContract`.
12. **IDs are immutable.** Renames write a new node plus a `redirects_to` tombstone at the
    old ID. Old citations must always resolve. Node IDs derive from the source URI, so a
    retitled document keeps its ID.
    → `Repository.tombstone` / `redirect` / `resolve`; `SyncEngine._node_id_for`;
    `TestDeletions`.
13. **Never overwrite human-authored content.** Machine writers touch only the interior of
    `<!-- cb:generated start … -->` fences, and only when the current content matches the
    recorded hash. Mismatch → divert to a proposal.
    → `store/fences.py`, `RegionTampered`.
14. **Writes are atomic.** temp file → fsync → rename. A partial store is never observable.
    → `LocalFsBackend.write_text`.
15. **Log node IDs, never node content.** No document text, no PII in logs, traces, or
    error messages — including exception payloads.
16. **All UI matches [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md).** Semantic Tailwind
    tokens only (no raw hex), `border-border/50`, `bg-black/5 dark:bg-white/5` for
    hover/fill, lucide icons at `strokeWidth={1.5}`, every surface specified in both light
    and dark. New components extend that language; they don't introduce a second one.
17. **The UI never filters by permission.** It renders the ACL-projected response from the
    API. If the client is doing access control, the API has a bug.
    → every handler in `api/app.py` takes an `AccessFilter` dependency; `web/src/lib/api.ts`
    holds no filtering logic.

Two M2 rules that follow from the above and are enforced in `connectors/sync.py`:

- **A delete is a tombstone, never a file removal.** Inbound edges survive, so a citation
  issued before the delete resolves to "deleted on `<date>`" instead of dangling.
- **Orphaned evidence goes `stale`, not away.** When a re-extraction can no longer find the
  text a human-decided edge cited, the edge is demoted and re-proposed. Keeping it would
  cite deleted text; dropping it would hide that the graph was ever wrong. Human accept and
  reject decisions otherwise survive re-extraction — a queue that resets is Sisyphean.

## Conventions

**Composition happens in `app.py`.** Providers, grants, principals, and store roots are
chosen there and nowhere else. A new entry point calls `build_app()`; it does not assemble
its own `Repository` or pick its own extractor. This is why the CLI, the MCP server, the
API, and the acceptance suite provably share one configuration.

**Frontmatter.** Canonical YAML: sorted keys, block style, UTC RFC-3339 timestamps, LF
endings, no trailing whitespace, exactly one trailing newline. Emitted only through
`store.serialize` — never hand-rolled `yaml.dump`.

**Node IDs.** `<type_plural>/<slug>`, matching the file path under `store/`. Entity slugs
are human-chosen and stable. Document slugs are `<derived-title>-<blake2b6(source_uri)>`.
`schemas/ids.py` owns every transformation; `TYPE_PLURALS` is hand-written for import
cheapness and a test asserts it stays in sync with `NodeType`.

**Edges.** Frontmatter `relations` is authoritative and canonically sorted. Body wikilinks
(`[[people/sam-kaur]]`, `handoff_to:: [[teams/finance]]`) are the human surface and are
lifted into `relations` on ingest with `provenance: human`. Traversal weights live in
`retrieve/hybrid.py`; `mentions` is weighted low on purpose — it is the most common edge
and the least informative, and an unweighted walk drowns the answer in it.

**Evidence spans come from the API, not the model.** `extract/claude.py` asks for prose
*and* a tool call: `tool_choice: auto` plus citations returns cited text blocks carrying
API-computed character offsets, followed by a schema-validated `tool_use` block. Forcing
the tool suppresses citations; setting an output format rejects them outright. A
model-reported offset that lands on the wrong sentence is worse than none, because §11's
gates are only as good as the evidence a reviewer can check.

**Extraction cache.** Content-addressed on
`blake2b(content_sha256 ‖ prompt_version ‖ model_id ‖ decode_params)`, stored in
`store/_cache/extraction/` and **committed**. That commit is what lets CI run `--frozen`
without a key. Changing a prompt or model is a deliberate refresh producing a reviewed
diff — never an incidental side effect of another change.

**The rule-based extractor is a real component, not a mock.** It is the no-key fallback and
the frozen-mode baseline, and it is what keeps the suite free. Improve it rather than
routing around it.

**A connector owes three things, not one:** content (incremental, cursor-addressed),
existence (the full live id set, so deletes can be detected by enumeration), and
permissions (source membership mirrored into grants). Mirrored permissions are eventually
consistent by construction; the window between a source change and the next sync is a real
leak window, and the honest posture is to bound and report it, not to claim it away.

**Document converters are pinned exactly** (`pypdf==6.7.1`, `python-docx==1.2.0`,
`mail-parser==4.1.2` in the `converters` group) and their versions recorded in each file's
`normalizer` block. A converter upgrade is a migration with a reviewed corpus diff, not a
routine dependency bump. Do not float these in `pyproject.toml`.

**LLM calls** go through `extract/claude.py` and `synthesize/claude.py` only. Model IDs are
module constants, never inlined at call sites. Prompt changes require bumping
`PROMPT_VERSION`, which changes every cache key — that is the point.

**Errors.** Fail closed on anything permission- or citation-related. Fail loud on
determinism violations. Degrade gracefully only on ranking quality.

## Adding things

- **A new source type** → a `connectors/` module (discovery, fetch, `acl_ref` derivation) +
  a `normalize/` module (pure) + fixtures in `corpus/synthetic/` + a determinism test.
  Never a special case inside an existing normalizer.
- **A new connector** → implement the `Connector` protocol in `connectors/base.py`:
  `fetch`, `enumerate_ids`, `grants`. `SyncEngine` is source-agnostic and stays untouched.
  Note where `enumerate_ids` stops being cheap and state the freshness SLA.
- **A new edge predicate** → add to the `Predicate` enum in `schemas/edges.py`, add a row
  to `GATES` and to the policy table in ARCHITECTURE §11, add a traversal weight in
  `retrieve/hybrid.py`, add at least one seeded golden question
  (`tests/acceptance/test_m1.py::SEEDED`) that depends on it.
- **A new node type** → `schemas/nodes.py` and `TYPE_PLURALS`, a store subdirectory, a
  resolution policy (or an explicit "no auto-merge"), and corpus fixtures.
- **A real index backend** → implement the `Index` protocol in `index/base.py`.
  `MemoryIndex` stays as the test double rather than being replaced.
- **A new UI component** → `web/src/components/ui/` in the DESIGN_SYSTEM language. Data
  comes in as props — no module-scope mock data. Controlled/uncontrolled dual API
  (`value ?? internalValue`).

## Current state

**M1 — done.** All five ROADMAP criteria pass:

| Criterion | Evidence |
|---|---|
| 10 seeded questions answered with correct citations | `TestSeededQuestions` |
| byte-identical re-ingestion | `TestDeterminism`, frozen cache, 0 misses, plus a concurrency case |
| rebuild-from-scratch matches the incremental index | `TestIndexRebuild` |
| permission separation; comp-channel canary never leaks | `TestPermissions`, at the retrieval **and** citation layers |
| `cb doctor` clean | store nodes = index nodes |

**M2 — the hard half, in simulation.** `SyncEngine` plus `SimulatedSlack` (a working
connector over mutable state, not a mock) covers what M2 claimed was difficult:

| M2 behaviour | Test |
|---|---|
| edit updates in place, same node ID, minimal diff | `TestEdits` |
| unchanged artifacts skip normalize and extract | `test_unchanged_channels_are_skipped_not_rewritten` |
| delete → tombstone, never a file removal | `TestDeletions` |
| human accept/reject survives re-extraction | `test_human_decisions_survive_re_extraction` |
| orphaned evidence → `stale`, not dropped | `test_orphaned_evidence_is_marked_stale_not_dropped` |
| leaving a channel revokes access next sync | `TestGrantSync` |
| revocation propagates to a delegated agent | `test_revocation_propagates_to_a_delegated_agent` |
| the leak window is real, bounded, and asserted | `test_the_leak_window_is_real_and_bounded_by_sync` |

**Verified this session, offline** (`COMPANY_BRAIN_OFFLINE=1`): the full suite — 177 tests
at the time of writing, 151 unit and 26 acceptance — passes in ~25s;
ruff, format, and `mypy --strict` clean. A cold ingest of the 201-file corpus yields 232
nodes, 364 chunks, 1122 accepted edges, and 32 edges pending review; `cb doctor` clean;
`cb sync` picks up 5 simulated channels. The online path is real, not theoretical — the
extraction cache in `store/` carries `model: claude-sonnet-5` frontmatter from live runs.

**What the green suite still does not prove.** The offline extractor shares assumptions
with the corpus generator — both know the same curated process list — so entity linking is
easier here than on real data. The hashing embedder has no semantic content; it is a
lexical trick with a vector interface, so `search_vector` behaves differently under
`OpenAIEmbedder`. The extractive fallback cannot hallucinate, which means invariant 11's
validator is exercised by construction but has never had to stop a real fabrication in CI.
And every M2 guarantee above holds against a simulated source whose `enumerate_ids()` is
free; against real Slack it is a paginated, rate-limited crawl, which is exactly where the
freshness SLA stops being a footnote.

**Not yet true, despite what a skim of this file suggests:** there are no git commits, so
"COMMITTED store" and `git diff --exit-code` describe the intent rather than the current
mechanism — determinism is verified by tree hashing inside the acceptance suite.
`tests/integration/` is empty. `resolve/` is empty.

**Next, in order:**

1. `supabase/` — `config.toml`, `migrations/*.sql`, and a `psycopg` `Index` implementation
   behind the existing protocol, with `tests/integration/` finally populated.
2. A real Slack connector: the same three protocol methods against the API, with paginated
   enumeration and a stated freshness SLA. Then Drive and Gmail.
3. Sensitivity tiers as physical store roots, and ARCHITECTURE §14 open questions 2 and 3
   (prod store backend, retention on delete) — both block the rest of M2.
4. M3 — entity resolution layer 3 in `resolve/`, and the review surfaces that depend on it.
