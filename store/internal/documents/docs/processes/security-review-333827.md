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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: b82420737cf4a5209649bfe106e4a52d
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/engineering
    object: teams/finance
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [463, 529]
        quote: Engineering hands off to Finance when a cost approval is required.
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [532, 605]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [64, 85]
        quote: '**Team:** Engineering'
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [233, 264]
        quote: Request is raised in Snowflake.
  - predicate: owns
    subject: people/tom-whelan
    object: processes/security-review
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [19, 63]
        quote: '**Owner:** Tom Whelan (tom@meridian.example)'
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
