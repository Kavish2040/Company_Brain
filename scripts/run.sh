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
  cmd_cb mcp serve "$@"
}

cmd_db() {
  # CLAUDE.md says `docker compose up -d postgres`; pyproject's integration marker
  # says `supabase start`. Neither is configured in the repo yet — say so plainly
  # rather than guessing which one wins.
  if [[ -f docker-compose.yml || -f compose.yaml ]]; then
    say "docker compose up -d postgres"; docker compose up -d postgres
  elif [[ -d supabase ]]; then
    say "supabase start"; supabase start
  else
    die "no local Postgres configured yet (no compose file, no supabase/). CLAUDE.md and pyproject.toml disagree on which it should be — resolve that before M1 integration tests."
  fi
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

  ${BOLD}cb${RESET} [args]     the company_brain CLI  ${DIM}(not implemented yet)${RESET}
  ${BOLD}api${RESET}           uvicorn, PORT=8000     ${DIM}(not implemented yet)${RESET}
  ${BOLD}mcp${RESET}           MCP server             ${DIM}(not implemented yet)${RESET}
  ${BOLD}db${RESET}            start local Postgres   ${DIM}(not configured yet)${RESET}

Examples:
  ./scripts/run.sh setup
  ./scripts/run.sh all
  ./scripts/run.sh test tests/unit -k serialize -q
  ./scripts/run.sh cb ask "who owns vendor renewals?"
EOF
  exit "${1:-1}"
}

main() {
  [[ $# -gt 0 ]] || usage 0
  local cmd="$1"; shift
  case "$cmd" in
    setup|check|fmt|test|unit|integration|acceptance|llm|all|cb|api|mcp|db) "cmd_$cmd" "$@" ;;
    -h|--help|help) usage 0 ;;
    *) printf '%sunknown command: %s%s\n\n' "$RED" "$cmd" "$RESET" >&2; usage 1 ;;
  esac
}

main "$@"
