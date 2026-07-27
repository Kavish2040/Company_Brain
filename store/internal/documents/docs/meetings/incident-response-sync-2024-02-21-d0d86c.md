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
        span: [116, 186]
        quote: "Ana Brito raised that incident response is still blocked on\n NetSuite."
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [116, 186]
        quote: "Ana Brito raised that incident response is still blocked on\n NetSuite."
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
