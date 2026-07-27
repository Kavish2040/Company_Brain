---
id: documents/email/re-customer-data-request-approval-needed-21dbc7
type: Document
title: 'Re: Customer data request ��� approval needed'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-012.eml
  external_id: email/thread-012.eml
  external_version: 9b8db2555c3c1713
  content_sha256: 9b8db2555c3c17135de40b6c125d51fe6941f969e7f224f2c21598907f3648ac
authors:
  - people/priya-raman
  - people/tom-whelan
timestamps:
  created: &id001 '2024-02-10T12:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 86f92bd80fcb00d402c455c8bbbe9f45
  status: accepted
relations:
  - predicate: authored_by
    object: people/priya-raman
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/tom-whelan
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: depends_on
    object: tools/datadog
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [164, 239]
        quote: Mei Tanaka owns this process, but the Datadog step is blocked on your team.
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [114, 123]
        quote: Hi Priya,
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [269, 287]
        quote: 'Thanks,

          Tom Whelan'
  - predicate: owns
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [164, 239]
        quote: Mei Tanaka owns this process, but the Datadog step is blocked on your team.
---

**From:** Tom Whelan <tom@meridian.example>

**To:** priya@meridian.example

**Date:** 2024-02-10T12:00:00+00:00

Hi Priya,

Following up on customer data request. Mei Tanaka owns this process, but the Datadog step is blocked on your team.

Can you confirm by Friday?

Thanks,
Tom Whelan
