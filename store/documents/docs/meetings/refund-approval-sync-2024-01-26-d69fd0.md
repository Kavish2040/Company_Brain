---
id: documents/docs/meetings/refund-approval-sync-2024-01-26-d69fd0
type: Document
title: Refund approval sync — 2024-01-26
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-26-refund-approval.md
  external_id: docs/meetings/2024-01-26-refund-approval.md
  external_version: 362ee4c1112cce2e
  content_sha256: 362ee4c1112cce2ec5a28190568f8d333328055225be4aec612228411e22b9d4
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 095a25bacbc2274e6984557c64ccf214
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [89, 98]
        quote: Ana Brito
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [64, 76]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [78, 87]
        quote: Sam Kelly
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [52, 62]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Refund approval
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [252, 263]
        quote: Engineering
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [241, 248]
        quote: Product
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [172, 180]
        quote: NetSuite
---

# Refund approval sync — 2024-01-26

**Attendees:** Tom Whelan, Nadia Hassan, Sam Kelly, Ana Brito

## Notes

- Tom Whelan raised that refund approval is still blocked on
 NetSuite.
- Ana Brito confirmed they own the process.
- Handoff from Product to Engineering is unclear; two
 tickets bounced back last week.

## Actions

- Ana Brito to document the handoff boundary.
