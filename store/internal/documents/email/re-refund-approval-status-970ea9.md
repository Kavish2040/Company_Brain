---
id: documents/email/re-refund-approval-status-970ea9
type: Document
title: 'Re: Refund approval ��� status'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-019.eml
  external_id: email/thread-019.eml
  external_version: 5d108e784ed7f5af
  content_sha256: 5d108e784ed7f5af461ae30873734d098c716639446e5d71af481de9480f027f
authors:
  - people/nadia-hassan
  - people/owen-fitz
timestamps:
  created: &id001 '2024-03-01T12:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: f615913cb31e6edc82dc0a4dd27e30a7
  status: accepted
relations:
  - predicate: authored_by
    object: people/nadia-hassan
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/owen-fitz
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
        span: [160, 169]
        quote: Ana Brito
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
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [57, 78]
        quote: owen@meridian.example
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [143, 158]
        quote: refund approval
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [197, 204]
        quote: Zendesk
---

**From:** Nadia Hassan <nadia@meridian.example>

**To:** owen@meridian.example

**Date:** 2024-03-01T12:00:00+00:00

Hi Owen,

Following up on refund approval. Ana Brito owns this process, but the Zendesk step is blocked on your team.

Can you confirm by Friday?

Thanks,
Nadia Hassan
