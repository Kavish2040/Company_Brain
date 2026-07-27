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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: ef26369260a3d6b8d1fa96c7e8647f64
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/quarterly-close
    object: tools/snowflake
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [145, 192]
        quote: "quarterly close is still blocked on\n Snowflake."
  - predicate: handoff_to
    subject: teams/finance
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [239, 323]
        quote: "Handoff from Finance to Engineering is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [195, 236]
        quote: Ana Brito confirmed they own the process.
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [117, 192]
        quote: "Owen Fitzgerald raised that quarterly close is still blocked on\n Snowflake."
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [37, 103]
        quote: '**Attendees:** Owen Fitzgerald, Ana Brito, Priya Raman, Tom Whelan'
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [339, 383]
        quote: Tom Whelan to document the handoff boundary.
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [145, 192]
        quote: "quarterly close is still blocked on\n Snowflake."
  - predicate: owns
    subject: people/ana-brito
    object: processes/quarterly-close
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [195, 236]
        quote: Ana Brito confirmed they own the process.
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
