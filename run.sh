#!/usr/bin/env bash
# company_brain — end-to-end demo.
#
#   ./run.sh          full pipeline + demo queries
#   ./run.sh test     lint, typecheck, unit + acceptance suites
#   ./run.sh clean    remove generated corpus and store
#
# Runs with no API keys and no database. Providers are chosen at startup:
# without ANTHROPIC_API_KEY / OPENAI_API_KEY it uses the deterministic offline
# extractor, embedder, and synthesizer. See src/company_brain/app.py.

set -euo pipefail
cd "$(dirname "$0")"

bold() { printf '\n\033[1m== %s\033[0m\n' "$1"; }
note() { printf '\033[2m%s\033[0m\n' "$1"; }

case "${1:-demo}" in
clean)
    rm -rf corpus/synthetic store
    echo "Removed corpus/synthetic and store/"
    exit 0
    ;;
test)
    bold "Lint"
    uv run ruff check .
    uv run ruff format --check .
    bold "Types (strict on schemas, acl, store)"
    uv run mypy
    bold "Unit tests"
    uv run pytest tests/unit -q
    bold "Acceptance suite (the M1 gate)"
    uv run pytest tests/acceptance -q -m acceptance
    exit 0
    ;;
demo) ;;
*)
    echo "usage: ./run.sh [demo|test|clean]" >&2
    exit 64
    ;;
esac

bold "0. Install"
uv sync --group dev --group converters --quiet
note "python $(uv run python -V 2>&1 | cut -d' ' -f2)"

bold "1. Generate the synthetic corpus"
uv run cb corpus --force
note "Meridian Logistics: ~60 people, 5 formats, 3 planted ambiguity traps"

bold "2. Ingest — normalize, extract, write the markdown store"
rm -rf store
uv run cb ingest

bold "3. Build the derived index"
uv run cb index

bold "4. Drift check"
uv run cb doctor

bold "5. Re-ingest, frozen — the M1 acceptance criterion"
BEFORE=$(find store -type f -exec shasum {} + | sort | shasum | cut -d' ' -f1)
uv run cb ingest --frozen >/dev/null
AFTER=$(find store -type f -exec shasum {} + | sort | shasum | cut -d' ' -f1)
if [[ "$BEFORE" == "$AFTER" ]]; then
    echo "PASS  markdown tree is byte-identical after re-ingestion ($BEFORE)"
else
    echo "FAIL  tree changed on re-ingest"
    exit 1
fi

bold "6. Who can see what"
uv run cb principals

bold "7. Ask — as the CEO"
uv run cb ask "who owns vendor renewals?" --principal ceo

bold "8. Ask — same question, as an external contractor"
note "Same query, narrower grants. The answer must differ, and must stay cited."
uv run cb ask "who owns vendor renewals?" --principal contractor

bold "9. The leak canary"
note "A restricted 'leadership-comp' channel exists. Only the CEO holds a grant."
echo "--- as ceo ---"
uv run cb ask "compensation bands for the engineering ladder" --principal ceo | head -8
echo "--- as eng-ic (must not surface it) ---"
uv run cb ask "compensation bands for the engineering ladder" --principal eng-ic | head -8

bold "10. MCP tool surface"
uv run cb mcp

bold "Done"
cat <<'EOF'
Store:  ./store            canonical markdown — open it in any editor
Corpus: ./corpus/synthetic  the 201 source files

  ./run.sh test    lint, types, and the full acceptance suite
  uv run cb ask "..." --principal ceo|support-lead|eng-ic|contractor
EOF
