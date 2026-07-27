---
id: documents/email/re-security-review-question-1464e0
type: Document
title: 'Re: Security review ��� question'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-001.eml
  external_id: email/thread-001.eml
  external_version: 7c95ae1f57038186
  content_sha256: 7c95ae1f5703818694d3b8828b109187457cfd1b81035827a56e8ca4444d653a
authors:
  - people/dev-oyelaran
  - people/nadia-hassan
timestamps:
  created: &id001 '2024-01-23T15:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 8087afbbfc7d46625d84ace8a9cf661f
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
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [158, 168]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [141, 156]
        quote: security review
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [196, 205]
        quote: PagerDuty
---

**From:** Nadia Hassan <nadia@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-01-23T15:00:00+00:00

Hi Dev,

Following up on security review. Tom Whelan owns this process, but the PagerDuty step is blocked on your team.

Can you confirm by Friday?

Thanks,
Nadia Hassan
