---
id: documents/email/re-customer-data-request-question-5f94d9
type: Document
title: 'Re: Customer data request ��� question'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-005.eml
  external_id: email/thread-005.eml
  external_version: 4725a9f6e2d0b861
  content_sha256: 4725a9f6e2d0b861c5494e309d0cfeed7a2a8c67b9d44f69b69cd8b81d39379a
authors:
  - people/sam-kelly
  - people/tom-whelan
timestamps:
  created: &id001 '2024-01-23T15:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 306e0bb47e9a31fdac5127e772dc98b1
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
  - predicate: depends_on
    subject: processes/data-request
    object: tools/zendesk
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [200, 240]
        quote: the Zendesk step is blocked on your team
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [53, 79]
        quote: sam.kelly@meridian.example
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [10, 20]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/data-request
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [127, 165]
        quote: Following up on customer data request.
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [200, 240]
        quote: the Zendesk step is blocked on your team
  - predicate: owns
    subject: people/mei-tanaka
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [166, 241]
        quote: Mei Tanaka owns this process, but the Zendesk step is blocked on your team.
---

**From:** Tom Whelan <tom@meridian.example>

**To:** sam.kelly@meridian.example

**Date:** 2024-01-23T15:00:00+00:00

Hi Sam,

Following up on customer data request. Mei Tanaka owns this process, but the Zendesk step is blocked on your team.

Can you confirm by Friday?

Thanks,
Tom Whelan
