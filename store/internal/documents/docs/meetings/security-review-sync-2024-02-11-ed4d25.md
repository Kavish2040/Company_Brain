---
id: documents/docs/meetings/security-review-sync-2024-02-11-ed4d25
type: Document
title: Security review sync — 2024-02-11
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-11-security-review.md
  external_id: docs/meetings/2024-02-11-security-review.md
  external_version: e722adc7cc2b8651
  content_sha256: e722adc7cc2b8651db90aa9ac658cc0205a69bba6d6b2258ed174e6fe9ab8482
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 0f21f2798ac4beb52295b6e9ea1fd7b8
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [76, 88]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [90, 102]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [52, 63]
        quote: Priya Raman
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [188, 198]
        quote: Tom Whelan
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [65, 74]
        quote: Zoë Ravel
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
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [246, 253]
        quote: Product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [257, 264]
        quote: Support
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [177, 184]
        quote: Zendesk
---

# Security review sync — 2024-02-11

**Attendees:** Priya Raman, Zoë Ravel, Dev Oyelaran, Nadia Hassan

## Notes

- Priya Raman raised that security review is still blocked on
 Zendesk.
- Tom Whelan confirmed they own the process.
- Handoff from Product to Support is unclear; two
 tickets bounced back last week.

## Actions

- Nadia Hassan to document the handoff boundary.
