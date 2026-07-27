---
id: documents/docs/decisions/decision-adjust-refund-approval-16cb8e
type: Document
title: 'Decision: adjust refund approval'
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/decisions/2024-02-14-refund-approval.md
  external_id: docs/decisions/2024-02-14-refund-approval.md
  external_version: 8784f52c895fa460
  content_sha256: 8784f52c895fa460a78a84bfdf230cfda61942ef2e99874205c54282d4a169fb
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 9c33b3ea223f1574967dd0ea8612aff2
  status: accepted
relations:
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [117, 174]
        quote: The existing refund approval process was taking too long.
  - predicate: supersedes
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [303, 373]
        quote: The previous informal arrangement documented in the Finance team page.
---

# Decision: adjust refund approval

**Date:** 2024-02-14
**Decided by:** Ana Brito
**Status:** accepted

## Context

The existing refund approval process was taking too long.

## Decision

Ana Brito will own refund approval going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the Finance team page.
