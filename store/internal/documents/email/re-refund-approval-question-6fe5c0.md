---
id: documents/email/re-refund-approval-question-6fe5c0
type: Document
title: 'Re: Refund approval ��� question'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-027.eml
  external_id: email/thread-027.eml
  external_version: 3fbe6693689423af
  content_sha256: 3fbe6693689423af61e3b366bfcab83a9288fce1b4c5735785ad3a927e171e14
authors:
  - people/dev-oyelaran
  - people/nadia-hassan
timestamps:
  created: &id001 '2024-01-23T11:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 952f0695e58f884ded3727d43efc7a97
  status: accepted
relations:
  - predicate: authored_by
    object: people/dev-oyelaran
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/nadia-hassan
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
        span: [158, 167]
        quote: Ana Brito
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [57, 77]
        quote: dev@meridian.example
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [24, 46]
        quote: nadia@meridian.example
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [141, 156]
        quote: refund approval
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [195, 204]
        quote: PagerDuty
---

**From:** Nadia Hassan <nadia@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-01-23T11:00:00+00:00

Hi Dev,

Following up on refund approval. Ana Brito owns this process, but the PagerDuty step is blocked on your team.

Can you confirm by Friday?

Thanks,
Nadia Hassan
