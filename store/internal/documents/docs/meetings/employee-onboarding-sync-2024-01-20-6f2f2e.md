---
id: documents/docs/meetings/employee-onboarding-sync-2024-01-20-6f2f2e
type: Document
title: Employee onboarding sync — 2024-01-20
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-20-onboarding.md
  external_id: docs/meetings/2024-01-20-onboarding.md
  external_version: a0d4578e2f214d1b
  content_sha256: a0d4578e2f214d1bedb6996acf3f5cd6f4c002cd02441292a239e3c9d460aee3
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 842ddfa8ea546747f9a5a400b804e8d3
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [56, 65]
        quote: Ana Brito
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [89, 101]
        quote: Dev Oyelaran
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
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [78, 87]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 21]
        quote: Employee onboarding
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [247, 258]
        quote: Engineering
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [262, 269]
        quote: Product
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [178, 186]
        quote: NetSuite
---

# Employee onboarding sync — 2024-01-20

**Attendees:** Ana Brito, Sam Kelly, Zoë Ravel, Dev Oyelaran

## Notes

- Ana Brito raised that employee onboarding is still blocked on
 NetSuite.
- Zoë Ravel confirmed they own the process.
- Handoff from Engineering to Product is unclear; two
 tickets bounced back last week.

## Actions

- Dev Oyelaran to document the handoff boundary.
