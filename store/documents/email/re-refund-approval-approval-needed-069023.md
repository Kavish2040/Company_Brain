---
id: documents/email/re-refund-approval-approval-needed-069023
type: Document
title: 'Re: Refund approval ��� approval needed'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-014.eml
  external_id: email/thread-014.eml
  external_version: dfb266bcfa3a99d2
  content_sha256: dfb266bcfa3a99d261949fc98054d9686ad86f4b355756368b44b9d257b4382d
authors:
  - people/sam-kelly
  - people/tom-whelan
timestamps:
  created: &id001 '2024-02-23T16:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: d0894b1af4a58cd686a0b4d86e879ee1
  status: accepted
relations:
  - predicate: authored_by
    object: people/sam-kelly
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/tom-whelan
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
        span: [160, 169]
        quote: Ana Brito
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [53, 79]
        quote: sam.kelly@meridian.example
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

**From:** Tom Whelan <tom@meridian.example>

**To:** sam.kelly@meridian.example

**Date:** 2024-02-23T16:00:00+00:00

Hi Sam,

Following up on refund approval. Ana Brito owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Tom Whelan
