---
id: documents/docs/meetings/capacity-planning-sync-2024-02-13-e437e0
type: Document
title: Capacity planning sync — 2024-02-13
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-13-capacity-planning.md
  external_id: docs/meetings/2024-02-13-capacity-planning.md
  external_version: b1e611800c0388c7
  content_sha256: b1e611800c0388c7ac38e6b71d9ed5ebb94f2360ee5b8d9c690109cfe36afdaf
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 855c36a9683d93a0e38af03ca87a1315
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [54, 63]
        quote: Ana Brito
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [88, 98]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [186, 201]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [75, 86]
        quote: Priya Raman
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [65, 73]
        quote: Sam Kaur
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 19]
        quote: Capacity planning
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [260, 271]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [249, 256]
        quote: Finance
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [173, 182]
        quote: Snowflake
---

# Capacity planning sync — 2024-02-13

**Attendees:** Ana Brito, Sam Kaur, Priya Raman, Mei Tanaka

## Notes

- Ana Brito raised that capacity planning is still blocked on
 Snowflake.
- Owen Fitzgerald confirmed they own the process.
- Handoff from Finance to Engineering is unclear; two
 tickets bounced back last week.

## Actions

- Mei Tanaka to document the handoff boundary.
