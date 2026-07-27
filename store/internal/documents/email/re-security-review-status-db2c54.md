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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: cc9164bd0cc8804a68260bfc4dc138a6
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
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [53, 73]
        quote: mei@meridian.example
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [22, 42]
        quote: tom@meridian.example
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [137, 152]
        quote: security review
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [192, 198]
        quote: Linear
---

**From:** Tom Whelan <tom@meridian.example>

**To:** mei@meridian.example

**Date:** 2024-02-28T11:00:00+00:00

Hi Mei,

Following up on security review. Tom Whelan owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Tom Whelan
