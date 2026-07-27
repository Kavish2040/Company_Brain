---
id: documents/docs/meetings/capacity-planning-sync-2024-01-24-4b153e
type: Document
title: Capacity planning sync — 2024-01-24
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-24-capacity-planning.md
  external_id: docs/meetings/2024-01-24-capacity-planning.md
  external_version: c8df2649e397c352
  content_sha256: c8df2649e397c352dec4ffecc982cac1e16ad4101cff4505632d8a009a60e69e
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 78efe0fdde6af2764d60a15e32f0acc2
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [87, 99]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [187, 202]
        quote: Owen Fitzgerald
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
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [54, 63]
        quote: Sam Kelly
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [75, 85]
        quote: Tom Whelan
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
        span: [261, 272]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [250, 257]
        quote: Finance
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [174, 183]
        quote: PagerDuty
---

# Capacity planning sync — 2024-01-24

**Attendees:** Sam Kelly, Sam Kaur, Tom Whelan, Nadia Hassan

## Notes

- Sam Kelly raised that capacity planning is still blocked on
 PagerDuty.
- Owen Fitzgerald confirmed they own the process.
- Handoff from Finance to Engineering is unclear; two
 tickets bounced back last week.

## Actions

- Nadia Hassan to document the handoff boundary.
