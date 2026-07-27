---
id: documents/docs/meetings/release-sign-off-sync-2024-02-07-66bc6c
type: Document
title: Release sign-off sync — 2024-02-07
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-07-release-signoff.md
  external_id: docs/meetings/2024-02-07-release-signoff.md
  external_version: 9bac790efce9f58f
  content_sha256: 9bac790efce9f58f45b39de1f1c7d26790308939729da2fabf67534f37392991
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 3d7733ac38e20bb42f5c28bf0b13ee7e
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [77, 89]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [53, 63]
        quote: Mei Tanaka
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
        span: [91, 100]
        quote: Sam Kelly
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [65, 75]
        quote: Tom Whelan
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
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [260, 267]
        quote: Support
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [175, 182]
        quote: Datadog
---

# Release sign-off sync — 2024-02-07

**Attendees:** Mei Tanaka, Tom Whelan, Dev Oyelaran, Sam Kelly

## Notes

- Mei Tanaka raised that release sign-off is still blocked on
 Datadog.
- Priya Raman confirmed they own the process.
- Handoff from Engineering to Support is unclear; two
 tickets bounced back last week.

## Actions

- Sam Kelly to document the handoff boundary.
