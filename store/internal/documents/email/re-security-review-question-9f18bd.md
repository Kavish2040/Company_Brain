---
id: documents/email/re-security-review-question-9f18bd
type: Document
title: 'Re: Security review ��� question'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-026.eml
  external_id: email/thread-026.eml
  external_version: 7352eef7fee18725
  content_sha256: 7352eef7fee18725d970692119d874abd8ead1f5bffb6a948ee5326d9d095687
authors:
  - people/tom-whelan
  - people/zoe-ravel
timestamps:
  created: &id001 '2024-03-03T12:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 8bde0db9ce2b6398f744bf9211522745
  status: accepted
relations:
  - predicate: authored_by
    object: people/tom-whelan
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/zoe-ravel
    confidence: 1.0
    provenance: structural
    status: accepted
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
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [53, 73]
        quote: zoe@meridian.example
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [137, 152]
        quote: security review
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [192, 200]
        quote: NetSuite
---

**From:** Tom Whelan <tom@meridian.example>

**To:** zoe@meridian.example

**Date:** 2024-03-03T12:00:00+00:00

Hi Zoë,

Following up on security review. Tom Whelan owns this process, but the NetSuite step is blocked on your team.

Can you confirm by Friday?

Thanks,
Tom Whelan
