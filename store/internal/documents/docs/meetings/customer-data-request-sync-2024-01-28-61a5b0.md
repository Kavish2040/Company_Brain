---
id: documents/docs/meetings/customer-data-request-sync-2024-01-28-61a5b0
type: Document
title: Customer data request sync — 2024-01-28
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-28-data-request.md
  external_id: docs/meetings/2024-01-28-data-request.md
  external_version: d3c236c209daa7c0
  content_sha256: d3c236c209daa7c07314d27930126092c152b464538cf362cf2df61646c78538
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: fe5629cab12bb740961633a907ca8411
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [85, 97]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [200, 210]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [99, 111]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [68, 83]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [58, 66]
        quote: Sam Kaur
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
        span: [258, 269]
        quote: Engineering
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [273, 280]
        quote: Support
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [189, 196]
        quote: Datadog
---

# Customer data request sync — 2024-01-28

**Attendees:** Sam Kaur, Owen Fitzgerald, Dev Oyelaran, Nadia Hassan

## Notes

- Sam Kaur raised that customer data request is still blocked on
 Datadog.
- Mei Tanaka confirmed they own the process.
- Handoff from Engineering to Support is unclear; two
 tickets bounced back last week.

## Actions

- Nadia Hassan to document the handoff boundary.
