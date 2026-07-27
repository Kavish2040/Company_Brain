---
id: documents/docs/meetings/quarterly-close-sync-2024-02-05-129939
type: Document
title: Quarterly close sync — 2024-02-05
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-05-quarterly-close.md
  external_id: docs/meetings/2024-02-05-quarterly-close.md
  external_version: 1326aac44a887730
  content_sha256: 1326aac44a887730e57ef8e335076aa4b76d403748aa8f6901808be76561708b
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 408e442ccfe80c06ffd9c1a3b77805a7
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [187, 196]
        quote: Ana Brito
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
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [65, 74]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Quarterly close
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [244, 251]
        quote: Product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [255, 262]
        quote: Support
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [177, 183]
        quote: Linear
---

# Quarterly close sync — 2024-02-05

**Attendees:** Priya Raman, Zoë Ravel, Dev Oyelaran, Nadia Hassan

## Notes

- Priya Raman raised that quarterly close is still blocked on
 Linear.
- Ana Brito confirmed they own the process.
- Handoff from Product to Support is unclear; two
 tickets bounced back last week.

## Actions

- Nadia Hassan to document the handoff boundary.
