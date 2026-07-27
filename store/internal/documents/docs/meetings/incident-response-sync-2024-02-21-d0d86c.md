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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: e4fd647a96fb7a65df65ef50f6548b79
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/incident-response
    object: tools/netsuite
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [138, 185]
        quote: "incident response is still blocked on\n NetSuite"
  - predicate: handoff_to
    subject: teams/support
    object: teams/product
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [239, 319]
        quote: "Handoff from Support to Product is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [116, 175]
        quote: Ana Brito raised that incident response is still blocked on
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [65, 77]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [335, 381]
        quote: Nadia Hassan to document the handoff boundary.
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [79, 88]
        quote: Zoë Ravel
  - predicate: owns
    subject: people/owen-fitz
    object: processes/incident-response
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [189, 236]
        quote: Owen Fitzgerald confirmed they own the process.
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
