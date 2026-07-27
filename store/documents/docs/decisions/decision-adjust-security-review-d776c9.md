---
id: documents/docs/decisions/decision-adjust-security-review-d776c9
type: Document
title: 'Decision: adjust security review'
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/decisions/2024-02-06-security-review.md
  external_id: docs/decisions/2024-02-06-security-review.md
  external_version: 4ac255b92b1132e1
  content_sha256: 4ac255b92b1132e1381808d070e2004275c05b2cdc6ceb5ca8cb199dd5fdd9ec
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 727287069b462a3175cf51cbfe95be56
  status: accepted
relations:
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [73, 83]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [19, 34]
        quote: security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [357, 368]
        quote: Engineering
---

# Decision: adjust security review

**Date:** 2024-02-06
**Decided by:** Tom Whelan
**Status:** accepted

## Context

The existing security review process was taking too long.

## Decision

Tom Whelan will own security review going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the Engineering team page.
