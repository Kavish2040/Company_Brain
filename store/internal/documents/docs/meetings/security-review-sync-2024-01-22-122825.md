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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 22494c224503eedb154aa8b29470e6ac
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/security-review
    object: tools/pagerduty
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [120, 195]
        quote: "Owen Fitzgerald raised that security review is still blocked on\n PagerDuty."
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [347, 393]
        quote: Dev Oyelaran to document the handoff boundary.
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [120, 195]
        quote: "Owen Fitzgerald raised that security review is still blocked on\n PagerDuty."
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [37, 106]
        quote: '**Attendees:** Owen Fitzgerald, Tom Whelan, Priya Raman, Dev Oyelaran'
  - predicate: mentions
    object: processes/security-review
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [2, 35]
        quote: Security review sync — 2024-01-22
  - predicate: owns
    subject: people/tom-whelan
    object: processes/security-review
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [198, 240]
        quote: Tom Whelan confirmed they own the process.
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
