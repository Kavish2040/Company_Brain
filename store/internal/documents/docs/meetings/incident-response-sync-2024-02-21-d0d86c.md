---
id: documents/docs/meetings/incident-response-sync-2024-02-21-d0d86c
type: Document
title: Incident response sync — 2024-02-21
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-21-incident-response.md
  external_id: docs/meetings/2024-02-21-incident-response.md
  external_version: d3e550ee4bb1d594
  content_sha256: d3e550ee4bb1d5948a1f6b20ed2aaaaa1666233c94c91b21bcab20a73b05dc7c
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 7e307eb53abe2fdbca7bd3bd170a7389
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [54, 63]
        quote: Ana Brito
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [65, 77]
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
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [189, 204]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [79, 88]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 19]
        quote: Incident response
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [263, 270]
        quote: Product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [252, 259]
        quote: Support
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [177, 185]
        quote: NetSuite
---

# Incident response sync — 2024-02-21

**Attendees:** Ana Brito, Dev Oyelaran, Zoë Ravel, Nadia Hassan

## Notes

- Ana Brito raised that incident response is still blocked on
 NetSuite.
- Owen Fitzgerald confirmed they own the process.
- Handoff from Support to Product is unclear; two
 tickets bounced back last week.

## Actions

- Nadia Hassan to document the handoff boundary.
