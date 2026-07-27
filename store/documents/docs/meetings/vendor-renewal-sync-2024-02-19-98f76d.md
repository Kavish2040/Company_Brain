---
id: documents/docs/meetings/vendor-renewal-sync-2024-02-19-98f76d
type: Document
title: Vendor renewal sync — 2024-02-19
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-19-vendor-renewal.md
  external_id: docs/meetings/2024-02-19-vendor-renewal.md
  external_version: 71bf05bdc854385b
  content_sha256: 71bf05bdc854385b97f449a9ce89ba32f06255d24fab92438a9722c3bc2c8b07
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: de1841a4a56d48e31a16c29e5ba6d1fb
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [76, 86]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [51, 63]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [88, 103]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [191, 199]
        quote: Sam Kaur
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
        span: [247, 254]
        quote: Product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [258, 265]
        quote: Support
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [178, 187]
        quote: PagerDuty
---

# Vendor renewal sync — 2024-02-19

**Attendees:** Nadia Hassan, Zoë Ravel, Mei Tanaka, Owen Fitzgerald

## Notes

- Nadia Hassan raised that vendor renewal is still blocked on
 PagerDuty.
- Sam Kaur confirmed they own the process.
- Handoff from Product to Support is unclear; two
 tickets bounced back last week.

## Actions

- Owen Fitzgerald to document the handoff boundary.
