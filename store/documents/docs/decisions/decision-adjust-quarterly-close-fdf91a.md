---
id: documents/docs/decisions/decision-adjust-quarterly-close-fdf91a
type: Document
title: 'Decision: adjust quarterly close'
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/decisions/2024-01-25-quarterly-close.md
  external_id: docs/decisions/2024-01-25-quarterly-close.md
  external_version: 4563168fd5b0c315
  content_sha256: 4563168fd5b0c315b12887989a022b4878e466a08bcfb05401f0223ca00f1a96
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 9c3260e788374b88532c6c2df19216b0
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
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [19, 34]
        quote: quarterly close
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

# Decision: adjust quarterly close

**Date:** 2024-01-25
**Decided by:** Ana Brito
**Status:** accepted

## Context

The existing quarterly close process was taking too long.

## Decision

Ana Brito will own quarterly close going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the Finance team page.
