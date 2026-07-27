# company_brain — project kickoff

## What we're building
company_brain ingests every artifact a company produces (docs, PDFs, email, Slack,
spreadsheets, meeting notes) and converts them into a single markdown knowledge
graph that both humans and AI agents read and write. On top of that substrate we
map the company as a system — people, processes, tools, and the handoffs between
them — and answer executive questions with evidence and citations.

Long-term product surface: an executive asks "where are handoffs between Support
and Engineering breaking down?" and gets a sourced answer in minutes instead of
commissioning a consulting engagement.

## Your task right now
Do NOT write application code yet. First produce:

1. `docs/ARCHITECTURE.md` — proposed system design with the tradeoffs you
   considered and rejected, not just the conclusion.
2. `CLAUDE.md` — repo conventions, stack, directory layout, how to run tests,
   invariants you must never break.
3. `docs/ROADMAP.md` — milestones M1–M5, each independently demoable.

Then stop and wait for my review before implementing.

## Constraints and opinions to design around

**Markdown is the canonical store, not a rendering of it.** Every ingested
artifact becomes a markdown file with YAML frontmatter (id, source, source_url,
authors, timestamps, acl, entity refs). Edges are expressed as typed wikilinks in
the body plus a frontmatter `relations` block. A human should be able to open the
repo in an editor and understand it. A derived index (Postgres) exists for query
speed but must be fully rebuildable from the markdown. If the index and the
markdown disagree, markdown wins.

**Permissions are load-bearing from day one, not a later feature.** Every node
carries an ACL inherited from its source (a private Slack DM stays private; a
Drive doc keeps its sharing scope). Every retrieval path — including agent tool
calls — filters by the requesting principal's access before ranking. Design this
into the schema now; retrofitting it means a rewrite, and one leaked comp
discussion kills an enterprise deal.

**Agents are first-class clients.** Expose the graph via an MCP server with tools
for search, traverse, read_node, write_node, propose_edge. Agent writes go to a
review queue by default, not straight into the graph.

**Retrieval is hybrid.** Vector search finds candidate nodes; graph traversal
expands context along typed edges; the synthesizer must cite specific node IDs.
An answer with no citations is a bug, not a degraded response.

## Stack (push back if you disagree, with reasons)
- Python 3.12, uv, FastAPI
- Postgres + pgvector as the derived index
- Markdown store on local FS for dev, S3-compatible object store for prod
- Pydantic models as the single source of truth for node/edge schemas
- pytest, with fixtures using a small synthetic company corpus

## Milestone 1 — the only thing that matters right now
One vertical slice, end to end:
- Ingest a directory of mixed local files (.md, .pdf, .docx, .eml, Slack export JSON)
- Normalize each to markdown + frontmatter, deterministically (same input → same
  output, so re-ingestion is idempotent and diffable in git)
- Extract entities (Person, Team, Tool, Process, Document, Decision) and typed
  edges (authored_by, mentions, owns, depends_on, handoff_to, supersedes)
- Persist to markdown store + build the Postgres index
- MCP server exposing search / traverse / read_node
- CLI: `company_brain ask "who owns vendor renewals?"` returns an answer with citations

Acceptance: against a synthetic 200-file corpus committed to the repo, the CLI
answers 10 seeded questions with correct citations, and full re-ingestion
produces a byte-identical markdown tree.

## Things I want you to flag, not silently solve
- Entity resolution: "Sam", "Sam K.", sam@co.com, @samk are one person. Tell me
  what you propose and where it will fail.
- What happens when a source document is deleted or edited upstream.
- Where you think the LLM extraction step will be unreliable enough to need a
  human-in-the-loop gate.

Start with ARCHITECTURE.md.