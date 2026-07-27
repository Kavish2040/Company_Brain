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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: fe63bb5454a89db85e46087b2557c43d
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/engineering
    object: teams/support
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [248, 332]
        quote: "Handoff from Engineering to Support is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [348, 391]
        quote: Zoë Ravel to document the handoff boundary.
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [124, 200]
        quote: "Nadia Hassan raised that customer data request is still blocked on\n Zendesk."
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [124, 200]
        quote: "Nadia Hassan raised that customer data request is still blocked on\n Zendesk."
  - predicate: owns
    subject: people/mei-tanaka
    object: processes/data-request
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [203, 245]
        quote: Mei Tanaka confirmed they own the process.
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
