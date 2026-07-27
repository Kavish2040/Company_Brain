---
id: documents/docs/meetings/quarterly-close-sync-2024-01-16-d870c7
type: Document
title: Quarterly close sync — 2024-01-16
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-16-quarterly-close.md
  external_id: docs/meetings/2024-01-16-quarterly-close.md
  external_version: ffb4e785a22299d0
  content_sha256: ffb4e785a22299d0671ba104aaa7710be9de753bfad7eb139432b5137d11b45e
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 5cd0056a3a1292237eec9d1b691c4288
  status: accepted
relations:
  - predicate: depends_on
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [137, 183]
        quote: "quarterly close is still blocked on\n NetSuite."
  - predicate: handoff_to
    object: teams/finance
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [230, 310]
        quote: "Handoff from Product to Finance is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [326, 370]
        quote: Mei Tanaka to document the handoff boundary.
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [112, 183]
        quote: "Nadia Hassan raised that quarterly close is still blocked on\n NetSuite."
  - predicate: owns
    object: processes/quarterly-close
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [186, 227]
        quote: Ana Brito confirmed they own the process.
---

# Quarterly close sync — 2024-01-16

**Attendees:** Nadia Hassan, Zoë Ravel, Ana Brito, Mei Tanaka

## Notes

- Nadia Hassan raised that quarterly close is still blocked on
 NetSuite.
- Ana Brito confirmed they own the process.
- Handoff from Product to Finance is unclear; two
 tickets bounced back last week.

## Actions

- Mei Tanaka to document the handoff boundary.
