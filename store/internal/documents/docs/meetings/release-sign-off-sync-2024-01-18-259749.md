---
id: documents/docs/meetings/release-sign-off-sync-2024-01-18-259749
type: Document
title: Release sign-off sync — 2024-01-18
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-18-release-signoff.md
  external_id: docs/meetings/2024-01-18-release-signoff.md
  external_version: fadb8b29e71240e4
  content_sha256: fadb8b29e71240e498ce5b4af77da2b201e0d828a2ce4061fb3a614061e43241
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 10f2466fae85866b332769df47c13830
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [75, 84]
        quote: Ana Brito
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [86, 101]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [186, 197]
        quote: Priya Raman
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [64, 73]
        quote: Sam Kelly
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [53, 62]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 18]
        quote: Release sign-off
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [245, 256]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [260, 267]
        quote: Finance
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [175, 182]
        quote: Zendesk
---

# Release sign-off sync — 2024-01-18

**Attendees:** Zoë Ravel, Sam Kelly, Ana Brito, Owen Fitzgerald

## Notes

- Zoë Ravel raised that release sign-off is still blocked on
 Zendesk.
- Priya Raman confirmed they own the process.
- Handoff from Engineering to Finance is unclear; two
 tickets bounced back last week.

## Actions

- Owen Fitzgerald to document the handoff boundary.
