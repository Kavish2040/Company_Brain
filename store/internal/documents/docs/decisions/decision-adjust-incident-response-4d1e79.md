---
id: documents/docs/decisions/decision-adjust-incident-response-4d1e79
type: Document
title: 'Decision: adjust incident response'
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/decisions/2024-01-17-incident-response.md
  external_id: docs/decisions/2024-01-17-incident-response.md
  external_version: 6c3c0062e874ecc9
  content_sha256: 6c3c0062e874ecc9c63e655ebffa5e731ae8fd21469207131d159876932943cc
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: f2eb9a836b5319c17e32af36ab1347da
  status: accepted
relations:
  - predicate: owns
    subject: people/owen-fitz
    object: processes/incident-response
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [199, 304]
        quote: 'Owen Fitzgerald will own incident response going forward, and the

          sign-off step moves to the owning team.'
  - predicate: supersedes
    object: teams/engineering
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [321, 395]
        quote: The previous informal arrangement documented in the Engineering team page.
---

# Decision: adjust incident response

**Date:** 2024-01-17
**Decided by:** Owen Fitzgerald
**Status:** accepted

## Context

The existing incident response process was taking too long.

## Decision

Owen Fitzgerald will own incident response going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the Engineering team page.
