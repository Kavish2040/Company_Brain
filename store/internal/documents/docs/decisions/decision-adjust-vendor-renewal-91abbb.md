---
id: documents/docs/decisions/decision-adjust-vendor-renewal-91abbb
type: Document
title: 'Decision: adjust vendor renewal'
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/decisions/2024-01-13-vendor-renewal.md
  external_id: docs/decisions/2024-01-13-vendor-renewal.md
  external_version: c607dd8ca15480c9
  content_sha256: c607dd8ca15480c9e57b9f395c992cf312f6e24cd3ef1bbf33d599b580a9a904
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 9ff04cc6317a00adc4925cc626419acc
  status: accepted
relations:
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [56, 80]
        quote: '**Decided by:** Sam Kaur'
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [115, 171]
        quote: The existing vendor renewal process was taking too long.
  - predicate: owns
    subject: people/sam-kaur
    object: processes/vendor-renewal
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [186, 281]
        quote: 'Sam Kaur will own vendor renewal going forward, and the

          sign-off step moves to the owning team.'
  - predicate: supersedes
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [298, 368]
        quote: The previous informal arrangement documented in the Finance team page.
---

# Decision: adjust vendor renewal

**Date:** 2024-01-13
**Decided by:** Sam Kaur
**Status:** accepted

## Context

The existing vendor renewal process was taking too long.

## Decision

Sam Kaur will own vendor renewal going forward, and the
sign-off step moves to the owning team.

## Supersedes

The previous informal arrangement documented in the Finance team page.
