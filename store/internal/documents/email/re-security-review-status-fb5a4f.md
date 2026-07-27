---
id: documents/email/re-security-review-status-fb5a4f
type: Document
title: 'Re: Security review ��� status'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-000.eml
  external_id: email/thread-000.eml
  external_version: fafe7d06de71d4e7
  content_sha256: fafe7d06de71d4e711689bdfd7f795e1a1a5a9fa4943a1bacf96fb4a2b06abdd
authors:
  - people/ana-brito
timestamps:
  created: &id001 '2024-01-21T13:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 67a3aedbc05d55f3d3bb7b610b4f6b62
  status: accepted
relations:
  - predicate: authored_by
    object: people/ana-brito
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
        span: [21, 41]
        quote: ana@meridian.example
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [153, 163]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [136, 151]
        quote: security review
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [191, 200]
        quote: PagerDuty
---

**From:** Ana Brito <ana@meridian.example>

**To:** ana@meridian.example

**Date:** 2024-01-21T13:00:00+00:00

Hi Ana,

Following up on security review. Tom Whelan owns this process, but the PagerDuty step is blocked on your team.

Can you confirm by Friday?

Thanks,
Ana Brito
