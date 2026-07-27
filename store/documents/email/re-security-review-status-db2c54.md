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
  prompt_version: claude-roster-v1
  cache_key: a7e5827734d2ac37013e05de7d789ae3
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
  - predicate: depends_on
    object: tools/linear
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [188, 227]
        quote: the Linear step is blocked on your team
  - predicate: owns
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
