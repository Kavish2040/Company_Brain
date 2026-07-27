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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 8cddcc73d6f0613b5005bd610250fd7e
  status: accepted
relations:
  - predicate: mentions
    object: teams/finance
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [303, 373]
        quote: The previous informal arrangement documented in the Finance team page.
  - predicate: owns
    subject: people/ana-brito
    object: processes/quarterly-close
    confidence: 0.97
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [189, 237]
        quote: Ana Brito will own quarterly close going forward
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
