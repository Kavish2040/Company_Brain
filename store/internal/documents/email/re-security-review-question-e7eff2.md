---
id: documents/email/re-security-review-question-e7eff2
type: Document
title: 'Re: Security review ��� question'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-002.eml
  external_id: email/thread-002.eml
  external_version: feb60428645ba92c
  content_sha256: feb60428645ba92cf013590f4891cef0d6672c0cc7764c8200aeb5705895e151
authors:
  - people/sam-kaur
  - people/zoe-ravel
timestamps:
  created: &id001 '2024-02-20T10:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: f0fb72aea0bed42fd4b13072a659d845
  status: accepted
relations:
  - predicate: authored_by
    object: people/sam-kaur
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/zoe-ravel
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [20, 45]
        quote: sam.kaur@meridian.example
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [157, 167]
        quote: Tom Whelan
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [56, 76]
        quote: zoe@meridian.example
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [140, 155]
        quote: security review
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [195, 201]
        quote: Linear
---

**From:** Sam Kaur <sam.kaur@meridian.example>

**To:** zoe@meridian.example

**Date:** 2024-02-20T10:00:00+00:00

Hi Zoë,

Following up on security review. Tom Whelan owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Sam Kaur
