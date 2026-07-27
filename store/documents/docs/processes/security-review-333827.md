---
id: documents/docs/processes/security-review-333827
type: Document
title: Security review
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/processes/security-review.md
  external_id: docs/processes/security-review.md
  external_version: 41d49dac7b0695d1
  content_sha256: 41d49dac7b0695d1f33edf285ccce204e2ba4ae5cb33fe3b60b3cd6763f47711
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: e62562919dbe3dd0dcf056ad572d0d62
  status: accepted
relations:
  - predicate: handoff_to
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [532, 564]
        quote: Support hands off to Engineering
  - predicate: handoff_to
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [463, 495]
        quote: Engineering hands off to Finance
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [42, 62]
        quote: tom@meridian.example
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [74, 85]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [488, 495]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [590, 597]
        quote: product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [532, 539]
        quote: Support
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [254, 263]
        quote: Snowflake
---

# Security review

**Owner:** Tom Whelan (tom@meridian.example)
**Team:** Engineering

## Purpose

The security review process governs how Meridian handles security review requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in Snowflake.
2. Engineering triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. Tom Whelan signs off before the request is closed.

## Handoffs

- Engineering hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
