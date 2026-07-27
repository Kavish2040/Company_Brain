---
id: documents/docs/meetings/vendor-renewal-sync-2024-01-10-f78532
type: Document
title: Vendor renewal sync — 2024-01-10
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-10-vendor-renewal.md
  external_id: docs/meetings/2024-01-10-vendor-renewal.md
  external_version: 3bca277d26fc6f64
  content_sha256: 3bca277d26fc6f644ff0fa33c62ccb2f25c9c57404212b5ebd701e92d3d2c157
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 2eae280119c38bee194fc494e03747b6
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [89, 101]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [63, 73]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [75, 87]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [187, 195]
        quote: Sam Kaur
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [51, 61]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 16]
        quote: Vendor renewal
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [254, 261]
        quote: Product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [243, 250]
        quote: Support
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [174, 183]
        quote: PagerDuty
---

# Vendor renewal sync — 2024-01-10

**Attendees:** Tom Whelan, Mei Tanaka, Nadia Hassan, Dev Oyelaran

## Notes

- Tom Whelan raised that vendor renewal is still blocked on
 PagerDuty.
- Sam Kaur confirmed they own the process.
- Handoff from Support to Product is unclear; two
 tickets bounced back last week.

## Actions

- Dev Oyelaran to document the handoff boundary.
