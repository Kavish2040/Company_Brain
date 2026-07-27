---
id: documents/docs/decisions/decision-adjust-release-sign-off-9cb44d
type: Document
title: 'Decision: adjust release sign-off'
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/decisions/2024-01-29-release-signoff.md
  external_id: docs/decisions/2024-01-29-release-signoff.md
  external_version: 5c8d089d24871fe0
  content_sha256: 5c8d089d24871fe0cc73852de437fde8619f3ed6552fca323884c1b268da79e1
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 4cbd0cb44bac878a293db051355188e6
  status: accepted
relations:
  - predicate: owns
    object: processes/release-signoff
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [193, 293]
        quote: 'Priya Raman will own release sign-off going forward, and the

          sign-off step moves to the owning team.'
  - predicate: supersedes
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [310, 384]
        quote: The previous informal arrangement documented in the Engineering team page.
---

# Decision: adjust release sign-off

**Date:** 2024-01-29
**Decided by:** Priya Raman
**Status:** accepted

## Context

The existing release sign-off process was taking too long.

## Decision

Priya Raman will own release sign-off going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the Engineering team page.
