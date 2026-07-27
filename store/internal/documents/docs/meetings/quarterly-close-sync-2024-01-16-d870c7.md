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
  prompt_version: claude-roster-v2
  cache_key: 245971176bb7518dc94accdf37246798
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [326, 370]
        quote: Mei Tanaka to document the handoff boundary.
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [37, 98]
        quote: '**Attendees:** Nadia Hassan, Zoë Ravel, Ana Brito, Mei Tanaka'
  - predicate: owns
    subject: people/ana-brito
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
