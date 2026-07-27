---
id: documents/email/re-capacity-planning-status-45f8ab
type: Document
title: 'Re: Capacity planning ��� status'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-021.eml
  external_id: email/thread-021.eml
  external_version: b819a8c1f0f22d77
  content_sha256: b819a8c1f0f22d77f5727aa4adb99bbc12bda749bda7abb301bb453585bec31c
authors:
  - people/priya-raman
  - people/tom-whelan
timestamps:
  created: &id001 '2024-02-24T13:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: ea6449500a9c225239916d672a87c1e7
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
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [160, 175]
        quote: Owen Fitzgerald
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
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [141, 158]
        quote: capacity planning
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [203, 210]
        quote: Datadog
---

**From:** Tom Whelan <tom@meridian.example>

**To:** priya@meridian.example

**Date:** 2024-02-24T13:00:00+00:00

Hi Priya,

Following up on capacity planning. Owen Fitzgerald owns this process, but the Datadog step is blocked on your team.

Can you confirm by Friday?

Thanks,
Tom Whelan
