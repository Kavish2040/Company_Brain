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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 7c36b63dbb2e10878a41af3fa4857c8b
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/data-request
    object: tools/datadog
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [125, 197]
        quote: "Sam Kaur raised that customer data request is still blocked on\n Datadog."
  - predicate: handoff_to
    subject: teams/engineering
    object: teams/support
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [245, 329]
        quote: "Handoff from Engineering to Support is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [43, 111]
        quote: '**Attendees:** Sam Kaur, Owen Fitzgerald, Dev Oyelaran, Nadia Hassan'
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [200, 242]
        quote: Mei Tanaka confirmed they own the process.
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [43, 111]
        quote: '**Attendees:** Sam Kaur, Owen Fitzgerald, Dev Oyelaran, Nadia Hassan'
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [43, 111]
        quote: '**Attendees:** Sam Kaur, Owen Fitzgerald, Dev Oyelaran, Nadia Hassan'
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.95
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [125, 197]
        quote: "Sam Kaur raised that customer data request is still blocked on\n Datadog."
  - predicate: mentions
    object: teams/engineering
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [245, 329]
        quote: "Handoff from Engineering to Support is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: teams/support
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [245, 329]
        quote: "Handoff from Engineering to Support is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [125, 197]
        quote: "Sam Kaur raised that customer data request is still blocked on\n Datadog."
  - predicate: owns
    subject: people/mei-tanaka
    object: processes/data-request
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [200, 242]
        quote: Mei Tanaka confirmed they own the process.
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
