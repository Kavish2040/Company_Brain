---
id: documents/email/re-refund-approval-approval-needed-ead123
type: Document
title: 'Re: Refund approval ��� approval needed'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-018.eml
  external_id: email/thread-018.eml
  external_version: 3f28b97631304cd9
  content_sha256: 3f28b97631304cd96a44e53dd1d1152d48397b5b2af5397b7cfcc516f9b6a33e
authors:
  - people/ana-brito
  - people/owen-fitz
timestamps:
  created: &id001 '2024-03-06T13:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 72b0a4aaaa7ea061ec618a51852fcbe1
  status: accepted
relations:
  - predicate: authored_by
    object: people/ana-brito
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/owen-fitz
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: depends_on
    subject: processes/refund-approval
    object: tools/linear
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [193, 232]
        quote: the Linear step is blocked on your team
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [127, 159]
        quote: Following up on refund approval.
  - predicate: mentions
    object: tools/linear
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [193, 232]
        quote: the Linear step is blocked on your team
  - predicate: owns
    subject: people/ana-brito
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [160, 233]
        quote: Ana Brito owns this process, but the Linear step is blocked on your team.
---

**From:** Owen Fitzgerald <owen@meridian.example>

**To:** ana@meridian.example

**Date:** 2024-03-06T13:00:00+00:00

Hi Ana,

Following up on refund approval. Ana Brito owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Owen Fitzgerald
