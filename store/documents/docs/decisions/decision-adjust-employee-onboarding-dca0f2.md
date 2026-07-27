---
id: documents/docs/decisions/decision-adjust-employee-onboarding-dca0f2
type: Document
title: 'Decision: adjust employee onboarding'
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/decisions/2024-02-02-onboarding.md
  external_id: docs/decisions/2024-02-02-onboarding.md
  external_version: 66555526af413e39
  content_sha256: 66555526af413e39af0b95fe31e8b46c66761a352e9c571a5c2e2a1975aaf76f
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: fc1c98dca4e2904f4109246f5bcead0a
  status: accepted
relations:
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [77, 86]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [19, 38]
        quote: employee onboarding
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [367, 374]
        quote: Product
---

# Decision: adjust employee onboarding

**Date:** 2024-02-02
**Decided by:** Zoë Ravel
**Status:** accepted

## Context

The existing employee onboarding process was taking too long.

## Decision

Zoë Ravel will own employee onboarding going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the Product team page.
