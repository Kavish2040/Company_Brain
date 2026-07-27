---
id: documents/docs/meetings/quarterly-close-sync-2024-01-16-d870c7
type: Document
title: Quarterly close sync — 2024-01-16
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-16-quarterly-close.md
  external_id: docs/meetings/2024-01-16-quarterly-close.md
  external_version: ffb4e785a22299d0
  content_sha256: ffb4e785a22299d0671ba104aaa7710be9de753bfad7eb139432b5137d11b45e
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 35a1e319a1eedc17e6a61d0b1f81822f
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [77, 86]
        quote: Ana Brito
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [88, 98]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [52, 64]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [66, 75]
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
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [254, 261]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [243, 250]
        quote: Product
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [174, 182]
        quote: NetSuite
---

# Quarterly close sync — 2024-01-16

**Attendees:** Nadia Hassan, Zoë Ravel, Ana Brito, Mei Tanaka

## Notes

- Nadia Hassan raised that quarterly close is still blocked on
 NetSuite.
- Ana Brito confirmed they own the process.
- Handoff from Product to Finance is unclear; two
 tickets bounced back last week.

## Actions

- Mei Tanaka to document the handoff boundary.
