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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: dc66f8581b8abd1f8797abbd8e11fe05
  status: accepted
relations:
  - predicate: authored_by
    object: people/nadia-hassan
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: depends_on
    subject: processes/capacity-planning
    object: tools/netsuite
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [164, 245]
        quote: Owen Fitzgerald owns this process, but the NetSuite step is blocked on your team.
  - predicate: owns
    subject: people/owen-fitz
    object: processes/capacity-planning
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [164, 245]
        quote: Owen Fitzgerald owns this process, but the NetSuite step is blocked on your team.
---

**From:** Nadia Hassan <nadia@meridian.example>

**To:** nadia@meridian.example

**Date:** 2024-02-19T12:00:00+00:00

Hi Nadia,

Following up on capacity planning. Owen Fitzgerald owns this process, but the NetSuite step is blocked on your team.

Can you confirm by Friday?

Thanks,
Nadia Hassan
