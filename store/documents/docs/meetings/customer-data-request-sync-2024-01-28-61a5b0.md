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
  prompt_version: claude-roster-v1
  cache_key: dc8a0ab353fe6c987a6a74b69a65f8be
  status: accepted
relations:
  - predicate: owns
    object: processes/data-request
    confidence: 0.8
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
