---
id: documents/docs/meetings/customer-data-request-sync-2024-02-17-580005
type: Document
title: Customer data request sync — 2024-02-17
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-17-data-request.md
  external_id: docs/meetings/2024-02-17-data-request.md
  external_version: 59fdf85a789ca8ee
  content_sha256: 59fdf85a789ca8eec8de5d8c1a7d93a7107ec6cd57c1d4178c4867fe355619e3
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: dbce4d63764b78e53f8be2c6e6093335
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [89, 99]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [58, 70]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [72, 87]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [101, 110]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 23]
        quote: Customer data request
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [261, 272]
        quote: Engineering
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [276, 283]
        quote: Support
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [192, 199]
        quote: Zendesk
---

# Customer data request sync — 2024-02-17

**Attendees:** Nadia Hassan, Owen Fitzgerald, Mei Tanaka, Zoë Ravel

## Notes

- Nadia Hassan raised that customer data request is still blocked on
 Zendesk.
- Mei Tanaka confirmed they own the process.
- Handoff from Engineering to Support is unclear; two
 tickets bounced back last week.

## Actions

- Zoë Ravel to document the handoff boundary.
