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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 7a0e1f668fa9719efb6871469afddc3e
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [74, 85]
        quote: Priya Raman
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [19, 35]
        quote: release sign-off
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [362, 373]
        quote: Engineering
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
