---
id: documents/docs/meetings/incident-response-sync-2024-02-01-a47886
type: Document
title: Incident response sync — 2024-02-01
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-01-incident-response.md
  external_id: docs/meetings/2024-02-01-incident-response.md
  external_version: 36f5ee51932b0aeb
  content_sha256: 36f5ee51932b0aeb3aacb7f5c5142c3d764b267560927f1ad843c40fc92d0a56
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 45cd6896843e6667126ec8f763000a43
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
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [77, 87]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [186, 201]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [65, 75]
        quote: Tom Whelan
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [54, 63]
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
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [249, 260]
        quote: Engineering
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [264, 271]
        quote: Support
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [173, 182]
        quote: Snowflake
---

# Incident response sync — 2024-02-01

**Attendees:** Zoë Ravel, Tom Whelan, Mei Tanaka, Ana Brito

## Notes

- Zoë Ravel raised that incident response is still blocked on
 Snowflake.
- Owen Fitzgerald confirmed they own the process.
- Handoff from Engineering to Support is unclear; two
 tickets bounced back last week.

## Actions

- Ana Brito to document the handoff boundary.
