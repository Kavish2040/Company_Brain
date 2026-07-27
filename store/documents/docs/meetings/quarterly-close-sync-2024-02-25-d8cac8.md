---
id: documents/docs/meetings/quarterly-close-sync-2024-02-25-d8cac8
type: Document
title: Quarterly close sync — 2024-02-25
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-25-quarterly-close.md
  external_id: docs/meetings/2024-02-25-quarterly-close.md
  external_version: 4d6cdaed1e6747a3
  content_sha256: 4d6cdaed1e6747a3a7e56cfcf435ca81f5ea8080b466faef74fa1926c1bbc766
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: efb6ea79f1430975d7478a6212909d57
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [69, 78]
        quote: Ana Brito
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [52, 67]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [80, 91]
        quote: Priya Raman
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [93, 103]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Quarterly close
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [263, 274]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [252, 259]
        quote: Finance
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [182, 191]
        quote: Snowflake
---

# Quarterly close sync — 2024-02-25

**Attendees:** Owen Fitzgerald, Ana Brito, Priya Raman, Tom Whelan

## Notes

- Owen Fitzgerald raised that quarterly close is still blocked on
 Snowflake.
- Ana Brito confirmed they own the process.
- Handoff from Finance to Engineering is unclear; two
 tickets bounced back last week.

## Actions

- Tom Whelan to document the handoff boundary.
