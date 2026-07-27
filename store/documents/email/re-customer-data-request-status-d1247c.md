---
id: documents/email/re-customer-data-request-status-d1247c
type: Document
title: 'Re: Customer data request ��� status'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-009.eml
  external_id: email/thread-009.eml
  external_version: 81ddd38cd81d9540
  content_sha256: 81ddd38cd81d954056d2f9c8fd5a95bb9c16057f49cf7bac3bf59c67876bd8f3
authors:
  - people/dev-oyelaran
  - people/zoe-ravel
timestamps:
  created: &id001 '2024-03-06T16:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: d4a2995be8fb7346c2f2f7a3ec4d6b15
  status: accepted
relations:
  - predicate: authored_by
    object: people/dev-oyelaran
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/zoe-ravel
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: depends_on
    object: tools/snowflake
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [194, 236]
        quote: the Snowflake step is blocked on your team
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [239, 265]
        quote: Can you confirm by Friday?
  - predicate: owns
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [160, 237]
        quote: Mei Tanaka owns this process, but the Snowflake step is blocked on your team.
---

**From:** Zo�� Ravel <zoe@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-03-06T16:00:00+00:00

Hi Dev,

Following up on customer data request. Mei Tanaka owns this process, but the Snowflake step is blocked on your team.

Can you confirm by Friday?

Thanks,
Zoë Ravel
