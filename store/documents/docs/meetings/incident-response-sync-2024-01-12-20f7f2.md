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
  prompt_version: claude-roster-v1
  cache_key: 76cf8a4eb069c082e68e4cf26043e97f
  status: accepted
relations:
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [339, 382]
        quote: Ana Brito to document the handoff boundary.
  - predicate: owns
    object: processes/incident-response
    confidence: 0.75
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
