---
id: documents/docs/meetings/incident-response-sync-2024-01-12-20f7f2
type: Document
title: Incident response sync — 2024-01-12
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-12-incident-response.md
  external_id: docs/meetings/2024-01-12-incident-response.md
  external_version: 22303f714789bf64
  content_sha256: 22303f714789bf648099e56b505a65234ee78d70101bf44098ca52258883cef1
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 908ee4a97573ef67f5bc75faca969a50
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/incident-response
    object: tools/datadog
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [115, 186]
        quote: "Priya Raman raised that incident response is still blocked on\n Datadog."
  - predicate: handoff_to
    subject: teams/engineering
    object: teams/support
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [239, 323]
        quote: "Handoff from Engineering to Support is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [339, 382]
        quote: Ana Brito to document the handoff boundary.
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [39, 101]
        quote: '**Attendees:** Priya Raman, Sam Kelly, Dev Oyelaran, Ana Brito'
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [115, 186]
        quote: "Priya Raman raised that incident response is still blocked on\n Datadog."
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [39, 101]
        quote: '**Attendees:** Priya Raman, Sam Kelly, Dev Oyelaran, Ana Brito'
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [115, 186]
        quote: "Priya Raman raised that incident response is still blocked on\n Datadog."
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [115, 186]
        quote: "Priya Raman raised that incident response is still blocked on\n Datadog."
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

# Incident response sync — 2024-01-12

**Attendees:** Priya Raman, Sam Kelly, Dev Oyelaran, Ana Brito

## Notes

- Priya Raman raised that incident response is still blocked on
 Datadog.
- Owen Fitzgerald confirmed they own the process.
- Handoff from Engineering to Support is unclear; two
 tickets bounced back last week.

## Actions

- Ana Brito to document the handoff boundary.
