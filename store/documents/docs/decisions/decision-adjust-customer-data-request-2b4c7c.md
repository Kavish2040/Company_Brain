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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 91c0a051230c2ab389ab9007a48776ba
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [79, 89]
        quote: Mei Tanaka
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [19, 40]
        quote: customer data request
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [375, 382]
        quote: Support
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
