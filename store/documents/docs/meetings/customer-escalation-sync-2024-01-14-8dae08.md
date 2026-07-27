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
  prompt_version: claude-roster-v1
  cache_key: 72ec83b3d4285451481f51b7e5312874
  status: accepted
relations:
  - predicate: depends_on
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [115, 189]
        quote: "Tom Whelan raised that customer escalation is still blocked on\n Snowflake."
  - predicate: handoff_to
    object: teams/product
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [239, 323]
        quote: "Handoff from Engineering to Product is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [41, 101]
        quote: '**Attendees:** Tom Whelan, Priya Raman, Zoë Ravel, Sam Kelly'
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [339, 382]
        quote: Sam Kelly to document the handoff boundary.
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.95
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [115, 189]
        quote: "Tom Whelan raised that customer escalation is still blocked on\n Snowflake."
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [41, 101]
        quote: '**Attendees:** Tom Whelan, Priya Raman, Zoë Ravel, Sam Kelly'
  - predicate: owns
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
