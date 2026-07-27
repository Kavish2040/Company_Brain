---
id: documents/docs/meetings/refund-approval-sync-2024-01-26-d69fd0
type: Document
title: Refund approval sync — 2024-01-26
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-26-refund-approval.md
  external_id: docs/meetings/2024-01-26-refund-approval.md
  external_version: 362ee4c1112cce2e
  content_sha256: 362ee4c1112cce2ec5a28190568f8d333328055225be4aec612228411e22b9d4
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 97e90372f3621479ca8004ccce119ef0
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/refund-approval
    object: tools/netsuite
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [112, 181]
        quote: "Tom Whelan raised that refund approval is still blocked on\n NetSuite."
  - predicate: handoff_to
    subject: teams/product
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [228, 312]
        quote: "Handoff from Product to Engineering is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [37, 98]
        quote: '**Attendees:** Tom Whelan, Nadia Hassan, Sam Kelly, Ana Brito'
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [37, 98]
        quote: '**Attendees:** Tom Whelan, Nadia Hassan, Sam Kelly, Ana Brito'
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [112, 181]
        quote: "Tom Whelan raised that refund approval is still blocked on\n NetSuite."
  - predicate: owns
    subject: people/ana-brito
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [184, 225]
        quote: Ana Brito confirmed they own the process.
---

# Refund approval sync — 2024-01-26

**Attendees:** Tom Whelan, Nadia Hassan, Sam Kelly, Ana Brito

## Notes

- Tom Whelan raised that refund approval is still blocked on
 NetSuite.
- Ana Brito confirmed they own the process.
- Handoff from Product to Engineering is unclear; two
 tickets bounced back last week.

## Actions

- Ana Brito to document the handoff boundary.
