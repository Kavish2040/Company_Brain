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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 7b098d6d1d60c421c9b8809081f9e96e
  status: accepted
relations:
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [72, 80]
        quote: Sam Kaur
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [19, 33]
        quote: vendor renewal
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [350, 357]
        quote: Finance
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
