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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 6102c3e027770c3ab5386cc0a1fddc79
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
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [59, 79]
        quote: ana@meridian.example
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [27, 48]
        quote: owen@meridian.example
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [143, 158]
        quote: refund approval
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [197, 203]
        quote: Linear
---

**From:** Owen Fitzgerald <owen@meridian.example>

**To:** ana@meridian.example

**Date:** 2024-03-06T13:00:00+00:00

Hi Ana,

Following up on refund approval. Ana Brito owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Owen Fitzgerald
