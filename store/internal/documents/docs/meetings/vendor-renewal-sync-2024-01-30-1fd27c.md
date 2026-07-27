---
id: documents/docs/meetings/vendor-renewal-sync-2024-01-30-1fd27c
type: Document
title: Vendor renewal sync — 2024-01-30
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-30-vendor-renewal.md
  external_id: docs/meetings/2024-01-30-vendor-renewal.md
  external_version: ef0400d87a7d535f
  content_sha256: ef0400d87a7d535f18be1beb6d064259007ab9af8bf5008fa5e3cce673288b06
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 19169ef155a79504f0d4d992ad3ebf0c
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [86, 95]
        quote: Ana Brito
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [51, 61]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [179, 187]
        quote: Sam Kaur
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [74, 84]
        quote: Tom Whelan
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [63, 72]
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
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [246, 257]
        quote: Engineering
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [235, 242]
        quote: Product
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [168, 175]
        quote: Zendesk
---

# Vendor renewal sync — 2024-01-30

**Attendees:** Mei Tanaka, Zoë Ravel, Tom Whelan, Ana Brito

## Notes

- Mei Tanaka raised that vendor renewal is still blocked on
 Zendesk.
- Sam Kaur confirmed they own the process.
- Handoff from Product to Engineering is unclear; two
 tickets bounced back last week.

## Actions

- Ana Brito to document the handoff boundary.
