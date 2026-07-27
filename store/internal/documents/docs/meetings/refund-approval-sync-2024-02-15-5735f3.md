---
id: documents/docs/meetings/refund-approval-sync-2024-02-15-5735f3
type: Document
title: Refund approval sync — 2024-02-15
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-15-refund-approval.md
  external_id: docs/meetings/2024-02-15-refund-approval.md
  external_version: 2fb45990da6154a9
  content_sha256: 2fb45990da6154a91997b6ee1ab2bfc4f6798759c4223894cd8deb45b116551f
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 9310323666c2c34808964c6ed26cf2b6
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
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [63, 73]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [86, 98]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [52, 61]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Refund approval
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
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [238, 245]
        quote: Support
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [171, 177]
        quote: Linear
---

# Refund approval sync — 2024-02-15

**Attendees:** Zoë Ravel, Mei Tanaka, Ana Brito, Nadia Hassan

## Notes

- Zoë Ravel raised that refund approval is still blocked on
 Linear.
- Ana Brito confirmed they own the process.
- Handoff from Support to Finance is unclear; two
 tickets bounced back last week.

## Actions

- Nadia Hassan to document the handoff boundary.
