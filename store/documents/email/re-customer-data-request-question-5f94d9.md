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
  prompt_version: claude-roster-v1
  cache_key: 45afb6230fab7b9219ab6321eb1a8aea
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
    object: tools/zendesk
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [166, 241]
        quote: Mei Tanaka owns this process, but the Zendesk step is blocked on your team.
  - predicate: owns
    object: people/mei-tanaka
    confidence: 0.95
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
