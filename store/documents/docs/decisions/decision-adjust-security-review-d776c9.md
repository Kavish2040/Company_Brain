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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 498657a7f118e13cdac468c7d544f262
  status: accepted
relations:
  - predicate: owns
    subject: people/tom-whelan
    object: processes/security-review
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [190, 288]
        quote: 'Tom Whelan will own security review going forward, and the

          sign-off step moves to the owning team.'
  - predicate: supersedes
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [305, 379]
        quote: The previous informal arrangement documented in the Engineering team page.
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
