---
id: documents/docs/meetings/customer-escalation-sync-2024-01-14-8dae08
type: Document
title: Customer escalation sync — 2024-01-14
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-14-customer-escalation.md
  external_id: docs/meetings/2024-01-14-customer-escalation.md
  external_version: bf88777ec4f728bc
  content_sha256: bf88777ec4f728bc4ee8d5f58cde174061b5ad8594bb1c1a176531a37dd6d21e
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 7126a32681b819f8a4d7b2a5fb621c89
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/customer-escalation
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [138, 189]
        quote: "customer escalation is still blocked on\n Snowflake."
  - predicate: owns
    subject: people/dev-oyelaran
    object: processes/customer-escalation
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [192, 236]
        quote: Dev Oyelaran confirmed they own the process.
---

# Customer escalation sync — 2024-01-14

**Attendees:** Tom Whelan, Priya Raman, Zoë Ravel, Sam Kelly

## Notes

- Tom Whelan raised that customer escalation is still blocked on
 Snowflake.
- Dev Oyelaran confirmed they own the process.
- Handoff from Engineering to Product is unclear; two
 tickets bounced back last week.

## Actions

- Sam Kelly to document the handoff boundary.
