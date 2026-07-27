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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: f337dcd3cf27ea45a33c4d0c62a4b272
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
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [19, 36]
        quote: incident response
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
