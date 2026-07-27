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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: cb904bfa6de6d2e0d7780718bb981812
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/incident-response
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [112, 183]
        quote: "Zoë Ravel raised that incident response is still blocked on\n Snowflake."
  - predicate: handoff_to
    subject: teams/engineering
    object: teams/support
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [236, 320]
        quote: "Handoff from Engineering to Support is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [336, 379]
        quote: Ana Brito to document the handoff boundary.
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [39, 98]
        quote: '**Attendees:** Zoë Ravel, Tom Whelan, Mei Tanaka, Ana Brito'
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [39, 98]
        quote: '**Attendees:** Zoë Ravel, Tom Whelan, Mei Tanaka, Ana Brito'
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [112, 183]
        quote: "Zoë Ravel raised that incident response is still blocked on\n Snowflake."
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [112, 183]
        quote: "Zoë Ravel raised that incident response is still blocked on\n Snowflake."
  - predicate: owns
    subject: people/owen-fitz
    object: processes/incident-response
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [186, 233]
        quote: Owen Fitzgerald confirmed they own the process.
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
