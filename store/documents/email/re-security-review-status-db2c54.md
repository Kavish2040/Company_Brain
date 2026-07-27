---
id: documents/email/re-security-review-status-db2c54
type: Document
title: 'Re: Security review ��� status'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-017.eml
  external_id: email/thread-017.eml
  external_version: 501b8d65e6ef3786
  content_sha256: 501b8d65e6ef37869e840557917afcdcd2a1341d252ebc3706f4f760122d8031
authors:
  - people/mei-tanaka
  - people/tom-whelan
timestamps:
  created: &id001 '2024-02-28T11:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 5928079f84b16af16e75710fd31c5290
  status: accepted
relations:
  - predicate: authored_by
    object: people/mei-tanaka
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/tom-whelan
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [112, 119]
        quote: Hi Mei,
  - predicate: mentions
    object: tools/linear
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [154, 228]
        quote: Tom Whelan owns this process, but the Linear step is blocked on your team.
  - predicate: owns
    subject: people/tom-whelan
    object: processes/security-review
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [154, 228]
        quote: Tom Whelan owns this process, but the Linear step is blocked on your team.
---

**From:** Tom Whelan <tom@meridian.example>

**To:** mei@meridian.example

**Date:** 2024-02-28T11:00:00+00:00

Hi Mei,

Following up on security review. Tom Whelan owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Tom Whelan
