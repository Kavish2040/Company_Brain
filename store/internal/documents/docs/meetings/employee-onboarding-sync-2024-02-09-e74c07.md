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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 5f08cb6b1f2e1782bcbf312703fb7511
  status: accepted
relations:
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [327, 370]
        quote: Sam Kelly to document the handoff boundary.
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [327, 370]
        quote: Sam Kelly to document the handoff boundary.
  - predicate: owns
    subject: people/zoe-ravel
    object: processes/onboarding
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [187, 228]
        quote: Zoë Ravel confirmed they own the process.
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
