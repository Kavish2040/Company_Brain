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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: c30ccec9e3163799e532f2fd54fd2a2f
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
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [164, 174]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [53, 75]
        quote: priya@meridian.example
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
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [141, 162]
        quote: customer data request
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [202, 209]
        quote: Datadog
---

**From:** Tom Whelan <tom@meridian.example>

**To:** priya@meridian.example

**Date:** 2024-02-10T12:00:00+00:00

Hi Priya,

Following up on customer data request. Mei Tanaka owns this process, but the Datadog step is blocked on your team.

Can you confirm by Friday?

Thanks,
Tom Whelan
