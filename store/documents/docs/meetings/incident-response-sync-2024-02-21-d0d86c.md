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
  prompt_version: claude-roster-v1
  cache_key: 7e22c3f19e2d9743a80b1d8f50099d5f
  status: accepted
relations:
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [335, 381]
        quote: Nadia Hassan to document the handoff boundary.
  - predicate: owns
    object: processes/incident-response
    confidence: 0.7
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
