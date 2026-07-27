---
id: documents/email/re-security-review-status-9aa3b3
type: Document
title: 'Re: Security review ��� status'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-013.eml
  external_id: email/thread-013.eml
  external_version: 05ca232d4efa182b
  content_sha256: 05ca232d4efa182b20e25c9a7dd06271dd4e0eaccded72f38a880ad3d7bf0dea
authors:
  - people/ana-brito
  - people/sam-kaur
timestamps:
  created: &id001 '2024-02-23T15:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 871c44143a822f4278db9b349b62efd3
  status: accepted
relations:
  - predicate: authored_by
    object: people/ana-brito
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/sam-kaur
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
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [52, 77]
        quote: sam.kaur@meridian.example
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
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [196, 203]
        quote: Zendesk
---

**From:** Ana Brito <ana@meridian.example>

**To:** sam.kaur@meridian.example

**Date:** 2024-02-23T15:00:00+00:00

Hi Sam,

Following up on security review. Tom Whelan owns this process, but the Zendesk step is blocked on your team.

Can you confirm by Friday?

Thanks,
Ana Brito
