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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: dd77f617655b6a30c87ff7fbf2ec7357
  status: accepted
relations:
  - predicate: supersedes
    object: teams/product
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [315, 385]
        quote: The previous informal arrangement documented in the Product team page.
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
