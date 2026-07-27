#!/usr/bin/env bash
# Dev entry point for company_brain. Every command runs through `uv run`, so the
# venv is created and synced on demand — no manual activation.
#
#   ./scripts/run.sh setup      install everything (deps + dev + pinned converters)
#   ./scripts/run.sh check      ruff + format + mypy (the CI lint gate)
#   ./scripts/run.sh test       pytest, minus live-LLM tests
#   ./scripts/run.sh all        check + test
#
# Run with no arguments for the full command list.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -t 1 ]]; then BOLD=$'\033[1m'; DIM=$'\033[2m'; RED=$'\033[31m'; RESET=$'\033[0m'
else BOLD=""; DIM=""; RED=""; RESET=""; fi

say()  { printf '%s==>%s %s\n' "$BOLD" "$RESET" "$*" >&2; }
die()  { printf '%s==>%s %s\n' "$RED" "$RESET" "$*" >&2; exit 1; }

need_uv() {
  command -v uv >/dev/null 2>&1 ||
    die "uv is not installed. See https://docs.astral.sh/uv/getting-started/installation/"
}

# The `cb` console script points at company_brain.cli.main:app, which does not
# exist during the design phase. Fail with that fact instead of a stack trace.
need_module() {
  local path="$1" what="$2"
  [[ -f "$path" ]] || die "$what is not implemented yet (missing $path). See docs/ROADMAP.md — M1."
}

cmd_setup() {
  need_uv
  # --all-groups pulls dev *and* the exactly-pinned converters group. The pins are
  # load-bearing: converter output is part of the canonical store (CLAUDE.md).
  say "uv sync --all-groups"
  uv sync --all-groups
  say "python: $(uv run python -c 'import sys; print(sys.version.split()[0])')"
  say "setup complete — try: ./scripts/run.sh all"
}

cmd_check() {
  need_uv
  say "ruff check"
  uv run ruff check .
  say "ruff format --check"
  uv run ruff format --check .
  # Only the packages CLAUDE.md marks strict; mypy's own config handles the rest.
  say "mypy (schemas, acl, store)"
  uv run mypy src/company_brain/schemas src/company_brain/acl src/company_brain/store
}

cmd_fmt() {
  need_uv
  say "ruff format"
  uv run ruff format .
  say "ruff check --fix"
  uv run ruff check --fix .
}

cmd_test()       { need_uv; uv run pytest "$@"; }
cmd_unit()       { need_uv; uv run pytest -m unit "$@"; }
cmd_integration(){ need_uv; uv run pytest -m integration "$@"; }   # needs Postgres
cmd_acceptance() { need_uv; uv run pytest -m acceptance "$@"; }    # the M1 gate
cmd_llm()        { need_uv; uv run pytest -m llm "$@"; }           # live model calls

cmd_all() { cmd_check; say "pytest"; cmd_test "$@"; }

cmd_cb() {
  need_uv
  need_module "src/company_brain/cli/main.py" "the cb CLI"
  uv run cb "$@"
}

cmd_api() {
  need_uv
  need_module "src/company_brain/api/app.py" "the FastAPI app"
  uv run uvicorn company_brain.api.app:app --reload --port "${PORT:-8000}"
}

cmd_mcp() {
  need_uv
  need_module "src/company_brain/mcp/server.py" "the MCP server"
  # stdout is the MCP transport; anything printed there corrupts the protocol.
  cmd_cb mcp --serve "$@"
}

cmd_web() {
  command -v npm >/dev/null 2>&1 || die "npm is not installed."
  [[ -d web/node_modules ]] || { say "npm install"; (cd web && npm install); }
  say "vite dev server on http://localhost:5173 (proxies /api to :8000)"
  (cd web && npm run dev)
}

# The demo: corpus -> ingest -> index -> re-ingest determinism -> ask, as two
# principals. Runs with or without API keys; app.py reports which providers it
# picked, so a run is never silently offline.
cmd_demo() {
  need_uv
  say "generate corpus"       ; uv run cb corpus --force
  say "ingest"                ; rm -rf store && uv run cb ingest
  say "index"                 ; uv run cb index
  say "doctor"                ; uv run cb doctor

  say "re-ingest, frozen (must be byte-identical)"
  local before after
  before=$(find store -type f -exec shasum {} + | sort | shasum | cut -d" " -f1)
  uv run cb ingest --frozen >/dev/null
  after=$(find store -type f -exec shasum {} + | sort | shasum | cut -d" " -f1)
  [[ "$before" == "$after" ]] || die "store changed on re-ingest"
  say "PASS byte-identical ($before)"

  say "who can see what"      ; uv run cb principals
  say "ask, as the CEO"       ; uv run cb ask "who owns vendor renewals?" --principal ceo
  say "ask, as a contractor"  ; uv run cb ask "who owns vendor renewals?" --principal contractor
  say "review queue"          ; uv run cb review stats
}

cmd_db() {
  # Supabase, not Docker Compose and not Alembic — see the stack table in CLAUDE.md.
  # Nothing in the codebase talks to a database yet; the M1 index is in-memory.
  command -v supabase >/dev/null 2>&1 ||
    die "the supabase CLI is not installed. See https://supabase.com/docs/guides/local-development"
  [[ -d supabase ]] ||
    die "no supabase/ directory yet (needs config.toml + migrations/*.sql). Nothing reads a database at M1 — see CLAUDE.md §Current state."
  say "supabase start"
  supabase start
}

usage() {
  cat >&2 <<EOF
${BOLD}company_brain${RESET} — dev commands

  ${BOLD}setup${RESET}         install deps: runtime + dev + pinned converters
  ${BOLD}check${RESET}         ruff check, ruff format --check, mypy strict
  ${BOLD}fmt${RESET}           ruff format and ruff check --fix
  ${BOLD}test${RESET} [args]   pytest (excludes live-LLM tests)
  ${BOLD}all${RESET}           check, then test

  ${BOLD}unit${RESET} | ${BOLD}integration${RESET} | ${BOLD}acceptance${RESET} | ${BOLD}llm${RESET}
                run one test marker (integration needs Postgres; llm needs an API key)

  ${BOLD}cb${RESET} [args]     the company_brain CLI
  ${BOLD}demo${RESET}          full pipeline end to end, then ask as two principals
  ${BOLD}api${RESET}           uvicorn on PORT (default 8000)
  ${BOLD}web${RESET}           vite dev server on :5173, proxying /api to :8000
  ${BOLD}mcp${RESET} [--as X]  MCP stdio server; identity is bound at startup
  ${BOLD}db${RESET}            start local Postgres   ${DIM}(not configured yet)${RESET}

Examples:
  ./scripts/run.sh setup
  ./scripts/run.sh all
  ./scripts/run.sh test tests/unit -k serialize -q
  ./scripts/run.sh cb ask "who owns vendor renewals?"
  ./scripts/run.sh api &  ./scripts/run.sh web
EOF
  exit "${1:-1}"
}

main() {
  [[ $# -gt 0 ]] || usage 0
  local cmd="$1"; shift
  case "$cmd" in
    setup|check|fmt|test|unit|integration|acceptance|llm|all|cb|api|web|mcp|db|demo) "cmd_$cmd" "$@" ;;
    -h|--help|help) usage 0 ;;
    *) printf '%sunknown command: %s%s\n\n' "$RED" "$cmd" "$RESET" >&2; usage 1 ;;
  esac
}

main "$@"
