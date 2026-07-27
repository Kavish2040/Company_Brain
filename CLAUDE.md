# CLAUDE.md — company_brain

Conventions and invariants for anyone (human or agent) working in this repo.
Design rationale lives in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); UI design
rules live in [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md); this file is the
operational contract. Read §Invariants before writing code.

## What this is

Ingests company artifacts (docs, PDFs, email, Slack, spreadsheets) into a markdown
knowledge graph that humans and agents both read and write, indexes it in Postgres for
query speed, and answers executive questions with citations to specific node IDs.

**Markdown is the database. Postgres is a rebuildable cache.**

## Stack

| Concern | Choice |
|---|---|
| Language | Python 3.12 |
| Packaging / env | uv (`uv sync`, `uv run`) |
| API | FastAPI |
| CLI | Typer, entry point `company_brain` (alias `cb`) |
| Index | **Supabase** Postgres + pgvector |
| Local stack | **`supabase start`** (Docker: Postgres, Storage, Auth, Studio) |
| Migrations | **Supabase CLI, plain SQL in `supabase/migrations/`** — hand-written, **not** generated from Pydantic, and **not** Alembic (two migration tools on one database is a footgun) |
| DB driver | `psycopg[binary,pool]` v3 direct — not `supabase-py`, which can't express the vector + FTS + RRF queries |
| Object store | Supabase Storage (S3-compatible), behind a `StoreBackend` protocol alongside local FS |
| Extraction | `claude-sonnet-5` (volume path, Batch API) |
| Synthesis | `claude-opus-5` |
| Embeddings | OpenAI `text-embedding-3-large` at **`dimensions=1536`** — pgvector's HNSW index caps at 2000 dims for `vector`, so native 3072 can't be indexed without `halfvec` |
| Schemas | Pydantic v2 — single source of truth for nodes/edges/frontmatter |
| Lexical search | Postgres FTS (`tsvector`) — no Elasticsearch |
| Tests | pytest + synthetic corpus fixtures |
| Lint / types | ruff, `mypy --strict` on `schemas/`, `acl/`, `store/` |
| Agent surface | MCP server |
| Frontend | React + TypeScript (strict), Tailwind, shadcn/ui in `components/ui/`, `lucide-react` |

Frontend lives in `web/`, separate from the Python package, and talks to the FastAPI
app over HTTP. No frontend code exists yet.

## Layout

```
src/company_brain/
  schemas/     Pydantic models: Node, Edge, ACL, Frontmatter, Principal. Nothing
               imports downward into other packages. Everything else imports this.
  connectors/  source-specific discovery + fetch + ACL ref derivation
  normalize/   bytes -> markdown + structural frontmatter. PURE. No LLM. No I/O
               beyond the input bytes.
  extract/     LLM entity/edge extraction, prompts, content-addressed cache
  resolve/     entity resolution: identity keys, aliases, candidate scoring
  store/       canonical markdown store: read, atomic write, canonical YAML emit,
               generated-region fences, tombstones
  index/       Postgres projection: build, incremental update, rebuild, doctor
  acl/         principals, grant sync, visible-set resolution, filter helpers
  retrieve/    hybrid candidate generation, RRF, graph expansion, rerank
  synthesize/  answer generation + citation validator
  review/      proposal queue: create, list, accept, reject
  mcp/         MCP server (search, traverse, read_node, write_node, propose_edge)
  api/         FastAPI app
  cli/         Typer commands
corpus/synthetic/    committed test corpus + seeded Q&A goldens
store/               generated markdown tree — COMMITTED, not gitignored: the M1
                     acceptance test is `git diff --exit-code` over this tree,
                     and store/_cache/ holds the committed extraction cache
supabase/            config.toml + migrations/*.sql
tests/               unit + integration + determinism + acceptance
docs/
```

Dependency direction is strictly downward: `schemas` ← everything; `store` never
imports `index`; `retrieve` never imports `store` (it reads through `index` and
`store`'s public read API). Circular imports are a design smell here, not a nuisance.

## Commands

```bash
uv sync --group dev                      # install
supabase start                           # local Postgres + pgvector + Storage
supabase db reset                        # apply migrations from scratch

uv run cb ingest ./corpus/synthetic      # normalize + extract + write store
uv run cb ingest ./corpus/synthetic --frozen   # fail on extraction cache miss (CI mode)
uv run cb index rebuild --from-scratch   # drop and rebuild the whole index
uv run cb doctor                         # store/index drift check; non-zero on drift
uv run cb ask "who owns vendor renewals?"
uv run cb review list | uv run cb review accept <id>
uv run cb mcp serve

uv run pytest                            # everything except live-LLM tests
uv run pytest -m llm                     # live model calls; not run in CI
uv run pytest -m acceptance              # the M1 gate: goldens + byte-identical re-ingest
uv run ruff check . && uv run ruff format --check .
uv run mypy src/company_brain/schemas src/company_brain/acl src/company_brain/store
```

Test markers: `unit` (default), `integration` (needs Postgres), `llm` (needs an API
key; excluded from CI), `acceptance`. CI runs `unit + integration + acceptance` with a
frozen extraction cache and never calls a model.

## Invariants

Breaking any of these is a revert, not a review comment.

1. **Markdown wins.** No code path writes to Postgres without the corresponding
   markdown write having succeeded first. There is no index-only state.
2. **The index is disposable.** `cb index rebuild --from-scratch` must fully reproduce
   the index from `store/` alone. It runs in CI on every PR. Anything that can't be
   rebuilt from markdown doesn't belong in the index (exceptions, by design:
   `principals`, `acl_grants`, `review_queue`, `ingest_runs`).
3. **Normalization is pure.** `normalize/` is a function of `(source bytes, normalizer
   version, config)` and nothing else. No wall-clock, no `uuid4`, no randomness, no
   locale-dependent formatting, no unordered iteration in output paths. Same input →
   byte-identical output, forever.
4. **No wall-clock timestamps in canonical files.** All timestamps come from the source
   artifact. Ingestion time belongs in `ingest_runs`.
5. **Every retrieval function takes an explicit `Principal`.** No default argument, no
   `None`, no `Optional`. Elevated access exists only via one audited helper in
   `acl/` and is never used in a request path.
6. **Never widen an ACL.** A derived node, summary, embedding, or proposal inherits the
   narrowest ACL of its inputs. Extraction cannot broaden visibility. This is enforced
   in the writer, not by convention.
7. **The store is not a permission boundary.** Enforcement is at API/MCP/CLI. Treat the
   whole store as classified at its most sensitive content. Never put production
   content on a dev machine.
8. **Principals are never a tool/API parameter.** Identity comes from the authenticated
   session. An agent's effective visibility is the intersection of its own grants and
   the invoking human's.
9. **Agents never write to the graph.** `write_node` and `propose_edge` create entries
   in `store/_proposals/` plus a `review_queue` row. Full stop.
10. **Every edge carries `provenance`, `confidence`, `evidence`, and `status`.** Only
    `status: accepted` edges are traversed at query time.
11. **Answers must cite.** The citation validator runs in the request path. Uncited or
    unresolvable-citation output is an error, never a degraded answer.
12. **IDs are immutable.** Renames write a new node plus a `redirects_to` tombstone at
    the old ID. Old citations must always resolve.
13. **Never overwrite human-authored content.** Machine writers touch only the interior
    of `<!-- cb:generated start … -->` fences, and only when the current content matches
    the recorded hash. Mismatch → divert to a proposal.
14. **Writes are atomic.** temp file → fsync → rename. A partial store is never
    observable.
15. **Log node IDs, never node content.** No document text, no PII in logs, traces, or
    error messages — including exception payloads.
16. **All UI matches [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md).** Semantic Tailwind
    tokens only (no raw hex), `border-border/50`, `bg-black/5 dark:bg-white/5` for
    hover/fill, lucide icons at `strokeWidth={1.5}`, every surface specified in both
    light and dark. New components extend that language; they don't introduce a second one.
17. **The UI never filters by permission.** It renders the ACL-projected response from
    the API. If the client is doing access control, the API has a bug.

## Conventions

**Frontmatter.** Canonical YAML: sorted keys, block style, UTC RFC-3339 timestamps, LF
endings, no trailing whitespace, exactly one trailing newline. Emitted only through
`store.serialize` — never hand-rolled `yaml.dump`.

**Node IDs.** `<type_plural>/<slug>`, matching the file path under `store/`. Entity
slugs are human-chosen and stable. Document slugs are
`<derived-title>-<blake2b6(source_uri)>`.

**Edges.** Frontmatter `relations` is authoritative. Body wikilinks
(`[[people/sam-kaur]]`, `handoff_to:: [[teams/finance]]`) are the human surface and are
lifted into `relations` on ingest with `provenance: human`.

**Extraction cache.** Content-addressed on
`blake2b(content_sha256 ‖ prompt_version ‖ model_id ‖ decode_params)`, stored in
`store/_cache/extraction/` and **committed**. Changing a prompt or model is a
deliberate `cb extract refresh` producing a reviewed diff — never an incidental side
effect of another change.

**Document converters are pinned exactly** and their versions recorded in each file's
`normalizer` block. A converter upgrade is a migration with a reviewed corpus diff, not
a routine dependency bump. Do not float these in `pyproject.toml`.

**LLM calls** go through `extract/client.py` only. Model IDs are config, never inlined.
Prompts live in `extract/prompts/` as versioned files; editing a prompt requires
bumping its version.

**Errors.** Fail closed on anything permission- or citation-related. Fail loud on
determinism violations. Degrade gracefully only on ranking quality.

## Adding things

- **A new source type** → a `connectors/` module (discovery, fetch, `acl_ref`
  derivation) + a `normalize/` module (pure) + fixtures in `corpus/synthetic/` + a
  determinism test. Never a special case inside an existing normalizer.
- **A new edge predicate** → add to the `Predicate` enum in `schemas/`, add a row to the
  gate policy table in ARCHITECTURE §11, add traversal weight in `retrieve/`, add at
  least one seeded golden question that depends on it.
- **A new node type** → `schemas/`, a store subdirectory, a resolution policy (or an
  explicit "no auto-merge"), and corpus fixtures.
- **A new UI component** → `web/components/ui/` via the shadcn CLI where one exists;
  otherwise hand-built in the DESIGN_SYSTEM language. Data comes in as props — no
  module-scope mock data. Controlled/uncontrolled dual API (`value ?? internalValue`).

## Current state

Design phase. `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and `docs/DESIGN_SYSTEM.md`
are written; no application code exists yet, pending review of the open questions in
ARCHITECTURE §14 and DESIGN_SYSTEM §8.
