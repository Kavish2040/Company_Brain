---
id: documents/docs/decisions/decision-adjust-customer-data-request-2b4c7c
type: Document
title: 'Decision: adjust customer data request'
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/decisions/2024-02-18-data-request.md
  external_id: docs/decisions/2024-02-18-data-request.md
  external_version: 9f2b3243b712d2a3
  content_sha256: 9f2b3243b712d2a34496d3714ce9661d7fc67419b4ce6cdeb4b204951efa1085
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 363bef249d220402c3d2f52145b22896
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [63, 89]
        quote: '**Decided by:** Mei Tanaka'
  - predicate: supersedes
    object: teams/support
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [323, 393]
        quote: The previous informal arrangement documented in the Support team page.
---

# Decision: adjust customer data request

**Date:** 2024-02-18
**Decided by:** Mei Tanaka
**Status:** accepted

## Context

The existing customer data request process was taking too long.

## Decision

Mei Tanaka will own customer data request going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the Support team page.
