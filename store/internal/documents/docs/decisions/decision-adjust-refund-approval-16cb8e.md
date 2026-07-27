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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: deb60c49d605c0c32ce82f1b5b33d07f
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [73, 82]
        quote: Ana Brito
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [19, 34]
        quote: refund approval
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [355, 362]
        quote: Finance
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
