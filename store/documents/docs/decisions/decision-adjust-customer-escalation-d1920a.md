---
id: documents/docs/decisions/decision-adjust-customer-escalation-d1920a
type: Document
title: 'Decision: adjust customer escalation'
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/decisions/2024-01-21-customer-escalation.md
  external_id: docs/decisions/2024-01-21-customer-escalation.md
  external_version: 7b5288a6a6c5fafd
  content_sha256: 7b5288a6a6c5fafd0fa1db481d42aa1cd6d1b2a6592109a0a3efa87d2ffcde0d
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 5b18c275e1bb9b1d1055f2ae012f7f57
  status: accepted
relations:
  - predicate: mentions
    object: teams/support
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [321, 391]
        quote: The previous informal arrangement documented in the Support team page.
  - predicate: supersedes
    object: processes/customer-escalation
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [321, 391]
        quote: The previous informal arrangement documented in the Support team page.
---

# Decision: adjust customer escalation

**Date:** 2024-01-21
**Decided by:** Dev Oyelaran
**Status:** accepted

## Context

The existing customer escalation process was taking too long.

## Decision

Dev Oyelaran will own customer escalation going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the Support team page.
