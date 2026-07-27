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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 78b7c0dae2cd5d8a0fae8057fb851c6a
  status: accepted
relations:
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [75, 90]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [19, 36]
        quote: capacity planning
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [373, 384]
        quote: Engineering
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
