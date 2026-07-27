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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: ad83c15e3fb7e16576f84ec91e7aba99
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/onboarding
    object: tools/netsuite
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [137, 187]
        quote: "employee onboarding is still blocked on\n NetSuite."
  - predicate: handoff_to
    subject: teams/engineering
    object: teams/product
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [234, 318]
        quote: "Handoff from Engineering to Product is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [115, 187]
        quote: "Ana Brito raised that employee onboarding is still blocked on\n NetSuite."
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [334, 380]
        quote: Dev Oyelaran to document the handoff boundary.
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [41, 101]
        quote: '**Attendees:** Ana Brito, Sam Kelly, Zoë Ravel, Dev Oyelaran'
  - predicate: owns
    subject: people/zoe-ravel
    object: processes/onboarding
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [190, 231]
        quote: Zoë Ravel confirmed they own the process.
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
