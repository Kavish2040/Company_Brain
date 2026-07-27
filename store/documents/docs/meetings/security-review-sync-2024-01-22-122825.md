---
id: documents/docs/meetings/security-review-sync-2024-01-22-122825
type: Document
title: Security review sync — 2024-01-22
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-22-security-review.md
  external_id: docs/meetings/2024-01-22-security-review.md
  external_version: 8905c2062a869c97
  content_sha256: 8905c2062a869c970e636f47d1ccd2187e23205709011db63d41154f8d08ebcb
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: db523d2a5667a1a9f60b723cdacc7d44
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [94, 106]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [52, 67]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [81, 92]
        quote: Priya Raman
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [69, 79]
        quote: Tom Whelan
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
        span: [256, 267]
        quote: Engineering
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [185, 194]
        quote: PagerDuty
---

# Security review sync — 2024-01-22

**Attendees:** Owen Fitzgerald, Tom Whelan, Priya Raman, Dev Oyelaran

## Notes

- Owen Fitzgerald raised that security review is still blocked on
 PagerDuty.
- Tom Whelan confirmed they own the process.
- Handoff from Engineering to Engineering is unclear; two
 tickets bounced back last week.

## Actions

- Dev Oyelaran to document the handoff boundary.
