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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: aba0fa7474f6d708e760205dceb9c2fa
  status: accepted
relations:
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [112, 178]
        quote: "Zoë Ravel raised that refund approval is still blocked on\n Linear."
  - predicate: owns
    subject: people/ana-brito
    object: processes/refund-approval
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [181, 222]
        quote: Ana Brito confirmed they own the process.
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
