---
id: documents/email/re-capacity-planning-status-4db95f
type: Document
title: 'Re: Capacity planning ��� status'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-023.eml
  external_id: email/thread-023.eml
  external_version: eb900af28d61db65
  content_sha256: eb900af28d61db65044cf5aa52bb627d1c7cad25dd1b7ce9ce2de23dc325e263
authors:
  - people/nadia-hassan
timestamps:
  created: &id001 '2024-02-19T12:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 67b50aa0a67d0a86dd77271cd331ea3c
  status: accepted
relations:
  - predicate: authored_by
    object: people/nadia-hassan
    confidence: 1.0
    provenance: structural
    status: accepted
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
        span: [164, 179]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [145, 162]
        quote: capacity planning
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [207, 215]
        quote: NetSuite
---

**From:** Nadia Hassan <nadia@meridian.example>

**To:** nadia@meridian.example

**Date:** 2024-02-19T12:00:00+00:00

Hi Nadia,

Following up on capacity planning. Owen Fitzgerald owns this process, but the NetSuite step is blocked on your team.

Can you confirm by Friday?

Thanks,
Nadia Hassan
