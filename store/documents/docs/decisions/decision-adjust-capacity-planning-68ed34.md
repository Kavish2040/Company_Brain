---
id: documents/docs/decisions/decision-adjust-capacity-planning-68ed34
type: Document
title: 'Decision: adjust capacity planning'
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/decisions/2024-02-10-capacity-planning.md
  external_id: docs/decisions/2024-02-10-capacity-planning.md
  external_version: 47c8760633b349e1
  content_sha256: 47c8760633b349e1efda4720ee77d1dc6049d0cf41112f81aa20cb6ba8a70390
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 320b521a17952bdbabee07209f6036df
  status: accepted
relations:
  - predicate: owns
    object: people/owen-fitz
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [199, 304]
        quote: 'Owen Fitzgerald will own capacity planning going forward, and the

          sign-off step moves to the owning team.'
  - predicate: owns
    object: processes/capacity-planning
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [199, 304]
        quote: 'Owen Fitzgerald will own capacity planning going forward, and the

          sign-off step moves to the owning team.'
  - predicate: supersedes
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [321, 395]
        quote: The previous informal arrangement documented in the Engineering team page.
---

# Decision: adjust capacity planning

**Date:** 2024-02-10
**Decided by:** Owen Fitzgerald
**Status:** accepted

## Context

The existing capacity planning process was taking too long.

## Decision

Owen Fitzgerald will own capacity planning going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the Engineering team page.
