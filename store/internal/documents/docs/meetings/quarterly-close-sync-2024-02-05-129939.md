---
id: documents/docs/meetings/quarterly-close-sync-2024-02-05-129939
type: Document
title: Quarterly close sync — 2024-02-05
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-05-quarterly-close.md
  external_id: docs/meetings/2024-02-05-quarterly-close.md
  external_version: 1326aac44a887730
  content_sha256: 1326aac44a887730e57ef8e335076aa4b76d403748aa8f6901808be76561708b
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: e7e0e886a98cb79dd6395ed1e517d541
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/quarterly-close
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [116, 184]
        quote: "Priya Raman raised that quarterly close is still blocked on\n Linear."
  - predicate: handoff_to
    subject: teams/product
    object: teams/support
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [231, 311]
        quote: "Handoff from Product to Support is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [37, 102]
        quote: '**Attendees:** Priya Raman, Zoë Ravel, Dev Oyelaran, Nadia Hassan'
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [327, 373]
        quote: Nadia Hassan to document the handoff boundary.
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [116, 184]
        quote: "Priya Raman raised that quarterly close is still blocked on\n Linear."
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [37, 102]
        quote: '**Attendees:** Priya Raman, Zoë Ravel, Dev Oyelaran, Nadia Hassan'
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [116, 184]
        quote: "Priya Raman raised that quarterly close is still blocked on\n Linear."
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [116, 184]
        quote: "Priya Raman raised that quarterly close is still blocked on\n Linear."
  - predicate: owns
    subject: people/ana-brito
    object: processes/quarterly-close
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [187, 228]
        quote: Ana Brito confirmed they own the process.
---

# Quarterly close sync — 2024-02-05

**Attendees:** Priya Raman, Zoë Ravel, Dev Oyelaran, Nadia Hassan

## Notes

- Priya Raman raised that quarterly close is still blocked on
 Linear.
- Ana Brito confirmed they own the process.
- Handoff from Product to Support is unclear; two
 tickets bounced back last week.

## Actions

- Nadia Hassan to document the handoff boundary.
