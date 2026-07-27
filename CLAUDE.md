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

**Status: M1 is complete and green.** The whole slice runs end to end — 201 synthetic
files become 232 nodes, retrieval answers with citations, ACLs are enforced at three
layers, uncited answers are refused. It runs **entirely offline**: no API key, no
database, no network. §Current state has what that costs and what M2 owes.

## Stack

The target stack. Rows marked ⏳ are decided but **not built** — do not assume they exist
when reading code; §Current state says what stands in for each today.

| Concern | Choice |
|---|---|
| Language | Python 3.12 |
| Packaging / env | uv (`uv sync --all-groups`, `uv run`) |
| CLI | Typer, entry point `company_brain` (alias `cb`) |
| Schemas | Pydantic v2 — single source of truth for nodes/edges/frontmatter |
| Store backend | `StoreBackend` protocol: local FS (dev), in-memory (tests), Supabase Storage |
| Agent surface | MCP server, stdio transport |
| Tests | pytest + a deterministically generated synthetic corpus |
| Lint / types | ruff, `mypy --strict` on `schemas/`, `acl/`, `store/` |
| ⏳ Index | **Supabase** Postgres + pgvector |
| ⏳ Local stack | **`supabase start`** (Docker: Postgres, Storage, Auth, Studio) |
| ⏳ Migrations | **Supabase CLI, plain SQL in `supabase/migrations/`** — hand-written, **not** generated from Pydantic, and **not** Alembic (two migration tools on one database is a footgun) |
| ⏳ DB driver | `psycopg[binary,pool]` v3 direct — not `supabase-py`, which can't express the vector + FTS + RRF queries |
| ⏳ Lexical search | Postgres FTS (`tsvector`) — no Elasticsearch |
| ⏳ Extraction | `claude-sonnet-5` (volume path, Batch API) |
| ⏳ Synthesis | `claude-opus-5` |
| ⏳ Embeddings | OpenAI `text-embedding-3-large` at **`dimensions=1536`** — pgvector's HNSW index caps at 2000 dims for `vector`, so native 3072 can't be indexed without `halfvec` |
| ⏳ API | FastAPI |
| ⏳ Frontend | React + TypeScript (strict), Tailwind, shadcn/ui in `components/ui/`, `lucide-react` |

Frontend lives in `web/`, separate from the Python package, and talks to the FastAPI app
over HTTP. No frontend code exists yet.

The offline/online decision is made in exactly one place — `choose_providers()` in
`app.py` — and it prints its reason on every `cb ingest`, so a run is never silently
offline. `index/base.py` already pins `EMBEDDING_DIMS = 1536`, so swapping the stand-in
embedder for `text-embedding-3-large` is a constructor change, not a reindex format change.

## Layout

```
src/company_brain/
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
  normalize/   bytes -> markdown + structural frontmatter. PURE. No LLM. No I/O beyond
               the input bytes. base.py (Normalizer, Registry) · formats.py (md/pdf/docx/eml/slack)
  extract/     base.py (Extractor protocol, CachedExtractor, content-addressed cache)
               rules.py (the deterministic offline extractor)
  connectors/  source-specific discovery + fetch + ACL ref derivation, and the ingest
               pipeline. local_fs.py is the only one so far.
  corpus/      generate.py — deterministic generator for the synthetic corpus
  index/       base.py (chunking, Embedder, Index protocol) · memory.py (the M1 index)
  acl/         grants.py — GrantTable, AccessFilter, the single audited elevate()
  retrieve/    hybrid.py — candidate generation, RRF, weighted graph expansion
  synthesize/  answer.py — synthesizer + citation validator
  review/      queue.py — proposal queue: list, accept, reject, per-predicate accept rate
  mcp/         server.py (Session, McpTools) · stdio.py (transport)
  cli/         main.py — Typer commands
  api/         FastAPI app — empty; lands with the UI
  resolve/     entity resolution: identity keys, aliases, candidate scoring — empty; M3
corpus/synthetic/    committed corpus (201 files), regenerable byte-identically
store/               generated markdown tree — COMMITTED, not gitignored: re-ingestion is
                     verified with `git diff --exit-code` over this tree, and
                     store/_cache/ holds the committed extraction cache
supabase/            config.toml + migrations/*.sql (not created yet)
scripts/run.sh       dev entry point: setup, check, test, all
tests/               unit/ · integration/ (empty until the database lands) · acceptance/
docs/
```

Dependency direction is strictly downward: `schemas` ← everything; `store` never imports
`index`; `retrieve` never imports `store` (it reads through `index` and `store`'s public
read API). Circular imports are a design smell here, not a nuisance. `app.py` is the one
exception by construction — it sits above everything and knows about all of it; CLI and
MCP import from it, never the reverse.

Heavy imports (`corpus.generate`, `connectors`, `review`) are deferred into command bodies
in `cli/main.py` so `cb --help` stays fast. Keep it that way.

## Commands

```bash
./scripts/run.sh setup                   # uv sync --all-groups: deps + dev + pinned converters
./scripts/run.sh all                     # ruff + format + mypy, then pytest
./scripts/run.sh test tests/unit -k acl  # pytest passthrough
```

`uv sync` alone does **not** install the `converters` group, and PDF/docx/email
normalization fails without it. Use `--all-groups`.

```bash
uv run cb corpus [--force]               # regenerate corpus/synthetic (deterministic)
uv run cb ingest corpus/synthetic        # normalize + extract + write store
uv run cb ingest corpus/synthetic --frozen     # fail on extraction cache miss (CI mode)
uv run cb index                          # rebuild the index and report its stats
uv run cb doctor                         # store/index drift check; non-zero on drift
uv run cb ask "who owns vendor renewals?" [--principal ceo|support-lead|eng-ic|contractor]
uv run cb principals                     # what each synthetic principal can see
uv run cb review list [--predicate owns] | uv run cb review stats
uv run cb review accept '<node_id>|<predicate>|<object>'
uv run cb mcp                            # print the tool contract as JSON
uv run cb mcp --serve --as ceo           # stdio MCP server; identity bound at startup

uv run pytest                            # everything except live-LLM tests
uv run pytest -m llm                     # live model calls; not run in CI
uv run pytest -m acceptance              # the M1 gate: goldens + byte-identical re-ingest

supabase start                           # ⏳ local Postgres + pgvector + Storage
supabase db reset                        # ⏳ apply migrations from scratch
```

Every `cb` command takes `--store PATH` (default `store/`).

Two things that surprise people:

- **`cb index` is a report, not a prerequisite.** The M1 index lives in memory and is
  rebuilt from markdown on every process start, so `cb ask` indexes before it answers.
  There is no incremental index and no persistent one yet. That is invariant 2 taken
  literally, and it stops being free somewhere north of this corpus size.
- **`cb ask` exit codes are load-bearing.** `2` = citation leak blocked, `3` = refused as
  uncited, `1` = ordinary failure. Never soften either into a printed warning.

Test markers: `unit` (default), `integration` (needs Postgres; no tests yet), `llm` (needs
an API key; excluded from CI), `acceptance`. CI runs `unit + integration + acceptance` with
a frozen extraction cache and never calls a model.

## Invariants

Breaking any of these is a revert, not a review comment. The pointer after each says where
it is enforced today — if you change that code, you are changing the contract.

1. **Markdown wins.** No code path writes to the index without the corresponding markdown
   write having succeeded first. There is no index-only state.
   → `connectors/local_fs.py` writes through `Repository`; `App.load_index` reads only `repo.walk()`.
2. **The index is disposable.** A from-scratch rebuild must fully reproduce the index from
   `store/` alone. It runs in CI on every PR. Anything that can't be rebuilt from markdown
   doesn't belong in the index (exceptions, by design: `principals`, `acl_grants`,
   `review_queue`, `ingest_runs`).
   → `App.load_index`; `tests/acceptance/test_m1.py::TestIndexRebuild`.
3. **Normalization is pure.** `normalize/` is a function of `(source bytes, normalizer
   version, config)` and nothing else. No wall-clock, no `uuid4`, no randomness, no
   locale-dependent formatting, no unordered iteration in output paths. Same input →
   byte-identical output, forever.
   → `TestDeterminism`. The corpus generator holds the same bar: fixed `SEED`, fixed
   `EPOCH`, zeroed zip mtimes in `normalize_zip`.
4. **No wall-clock timestamps in canonical files.** All timestamps come from the source
   artifact. Ingestion time belongs in `ingest_runs`.
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
8. **Principals are never a tool/API parameter.** Identity comes from the authenticated
   session. An agent's effective visibility is the intersection of its own grants and the
   invoking human's.
   → `mcp.server.Session(agent_id, delegated_by)`, bound by `cb mcp --as` at startup;
   `test_agent_visibility_is_intersected_with_the_human`.
9. **Agents never write to the graph.** `write_node` and `propose_edge` create entries in
   `store/_proposals/` plus a `review_queue` row. Full stop.
   → `McpTools.write_node` returns `state: pending_review`;
   `test_write_node_produces_a_proposal_not_a_mutation`.
10. **Every edge carries `provenance`, `confidence`, `evidence`, and `status`.** Only
    `status: accepted` edges are traversed at query time.
    → `schemas/edges.py`; `_llm_edges_cite` rejects an uncited LLM edge at construction;
    `GATES` / `decide_status` implement the ARCHITECTURE §11 policy table.
11. **Answers must cite.** The citation validator runs in the request path. Uncited or
    unresolvable-citation output is an error, never a degraded answer.
    → `synthesize.answer.validate` raises `UncitedAnswerError` / `CitationLeakError`;
    `TestCitationContract`.
12. **IDs are immutable.** Renames write a new node plus a `redirects_to` tombstone at the
    old ID. Old citations must always resolve.
    → `Repository.tombstone` / `redirect` / `resolve`.
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

Invariants 16–17 are unexercised — there is no `web/` yet.

## Conventions

**Composition happens in `app.py`.** Providers, grants, principals, and store roots are
chosen there and nowhere else. A new entry point calls `build_app()`; it does not assemble
its own `Repository` or pick its own extractor. This is why the CLI, the MCP server, and
the acceptance suite provably share one configuration.

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

**Extraction cache.** Content-addressed on
`blake2b(content_sha256 ‖ prompt_version ‖ model_id ‖ decode_params)`, stored in
`store/_cache/extraction/` and **committed**. Changing a prompt or model is a deliberate
`cb extract refresh` producing a reviewed diff — never an incidental side effect of another
change. `--frozen` turns a miss into an error, which is what lets the determinism tests
measure our pipeline instead of a provider's mood.

**The rule-based extractor is a real component, not a mock.** It is what makes CI free and
deterministic, and it remains the frozen-mode baseline after `claude-sonnet-5` extraction
lands. Improve it rather than routing around it.

**Document converters are pinned exactly** (`pypdf`, `python-docx`, `mail-parser` in the
`converters` group) and their versions recorded in each file's `normalizer` block. A
converter upgrade is a migration with a reviewed corpus diff, not a routine dependency
bump. Do not float these in `pyproject.toml`.

**LLM calls** go through `extract/client.py` only. Model IDs are config, never inlined.
Prompts live in `extract/prompts/` as versioned files; editing a prompt requires bumping
its version.

**Errors.** Fail closed on anything permission- or citation-related. Fail loud on
determinism violations. Degrade gracefully only on ranking quality.

## Adding things

- **A new source type** → a `connectors/` module (discovery, fetch, `acl_ref` derivation) +
  a `normalize/` module (pure) + fixtures in `corpus/synthetic/` + a determinism test.
  Never a special case inside an existing normalizer.
- **A new edge predicate** → add to the `Predicate` enum in `schemas/edges.py`, add a row
  to `GATES` and to the policy table in ARCHITECTURE §11, add a traversal weight in
  `retrieve/hybrid.py`, add at least one seeded golden question
  (`tests/acceptance/test_m1.py::SEEDED`) that depends on it.
- **A new node type** → `schemas/nodes.py` and `TYPE_PLURALS`, a store subdirectory, a
  resolution policy (or an explicit "no auto-merge"), and corpus fixtures.
- **A real index backend** → implement the `Index` protocol in `index/base.py`.
  `MemoryIndex` stays as the test double rather than being replaced.
- **A new UI component** → `web/components/ui/` via the shadcn CLI where one exists;
  otherwise hand-built in the DESIGN_SYSTEM language. Data comes in as props — no
  module-scope mock data. Controlled/uncontrolled dual API (`value ?? internalValue`).

## Current state

**M1 is done.** All five ROADMAP acceptance criteria pass:

| Criterion | Evidence |
|---|---|
| 10 seeded questions answered with correct citations | `TestSeededQuestions` |
| byte-identical re-ingestion | `TestDeterminism`, frozen cache, 0 misses |
| rebuild-from-scratch matches the incremental index | `TestIndexRebuild`, 232 nodes both ways |
| permission separation; comp-channel canary never leaks | `TestPermissions`, asserted at the retrieval **and** citation layers |
| `cb doctor` clean | 232 store nodes = 232 index nodes |

Shape of a run: 201 documents → 232 nodes, 364 chunks, 1122 accepted edges, 39 edges
pending human review. `ceo` sees 7 ACL refs, `contractor` 1, and the same question returns
visibly different, still-cited answers to each. 136 tests; the acceptance suite takes ~20s.

**What stands in for the ⏳ rows today** — all offline, all deterministic, all behind the
protocol the real thing will implement:

| Target | M1 stand-in |
|---|---|
| Supabase Postgres + pgvector | `MemoryIndex` — BM25 lexical + cosine, rebuilt per process |
| `text-embedding-3-large` @1536 | `HashingEmbedder` — same dimensionality, no model call |
| `claude-sonnet-5` extraction | `RuleBasedExtractor` — regex + a curated roster |
| `claude-opus-5` synthesis | `ExtractiveSynthesizer` — selects sentences, never generates prose |

**What the green suite does not prove.** The extractor shares assumptions with the corpus
generator — both know the same curated process list — so entity linking is easier here than
it will ever be on real data. The hashing embedder has no semantic content; it is a lexical
trick with a vector interface, and `search_vector` will behave differently the moment a real
embedder replaces it. Extractive synthesis cannot hallucinate, so invariant 11 has never had
to stop a real fabrication. M1 proves the skeleton holds, not that the answers are good.

**Next, in order:**

1. `supabase/` — `config.toml`, `migrations/*.sql`, and a `psycopg` `Index` implementation
   behind the existing protocol. `tests/integration/` stays empty until this lands.
2. Real providers behind `choose_providers`: the OpenAI embedder, then `claude-sonnet-5`
   extraction via the Batch API, with the rule-based path kept as the frozen-mode baseline.
3. Then M2 — live connectors, incremental sync, change and deletion handling, grant sync.

The FastAPI app and the `web/` frontend follow the API surface. The open questions in
ARCHITECTURE §14 and DESIGN_SYSTEM §8 are still open.
