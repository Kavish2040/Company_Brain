---
id: documents/docs/meetings/employee-onboarding-sync-2024-02-09-e74c07
type: Document
title: Employee onboarding sync — 2024-02-09
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-09-onboarding.md
  external_id: docs/meetings/2024-02-09-onboarding.md
  external_version: 668f864e9ecc28c9
  content_sha256: 668f864e9ecc28c92b6e9239df159170b65b20afda728f4dff97e406ef5889ee
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: ded63ef97eccb673b061f6e2ba57c6a1
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
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [78, 86]
        quote: Sam Kaur
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [88, 97]
        quote: Sam Kelly
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [67, 76]
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
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [255, 262]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [244, 251]
        quote: Product
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [174, 183]
        quote: PagerDuty
---

# Employee onboarding sync — 2024-02-09

**Attendees:** Ana Brito, Zoë Ravel, Sam Kaur, Sam Kelly

## Notes

- Ana Brito raised that employee onboarding is still blocked on
 PagerDuty.
- Zoë Ravel confirmed they own the process.
- Handoff from Product to Finance is unclear; two
 tickets bounced back last week.

## Actions

- Sam Kelly to document the handoff boundary.
