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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: ac8663df59022fe9a58ac55dfa89df91
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [92, 101]
        quote: Ana Brito
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [78, 90]
        quote: Dev Oyelaran
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
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [54, 65]
        quote: Priya Raman
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [67, 76]
        quote: Sam Kelly
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
        span: [252, 263]
        quote: Engineering
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [267, 274]
        quote: Support
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [178, 185]
        quote: Datadog
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
