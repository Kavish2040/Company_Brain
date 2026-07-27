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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: ca639748485d0959f5dd5c26c77a5aa5
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [192, 204]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [68, 79]
        quote: Priya Raman
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [92, 101]
        quote: Sam Kelly
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [56, 66]
        quote: Tom Whelan
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [81, 90]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 21]
        quote: Customer escalation
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
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [267, 274]
        quote: Product
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [179, 188]
        quote: Snowflake
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
