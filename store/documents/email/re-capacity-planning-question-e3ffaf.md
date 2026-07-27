---
id: documents/email/re-capacity-planning-question-e3ffaf
type: Document
title: 'Re: Capacity planning ��� question'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-008.eml
  external_id: email/thread-008.eml
  external_version: 025a893441f254e2
  content_sha256: 025a893441f254e21891f7606fbff5269daefea04da9c342ef58d2dd47d7226e
authors:
  - people/mei-tanaka
  - people/owen-fitz
timestamps:
  created: &id001 '2024-02-28T14:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: c412f5a2dd6e6603e8d7e8c0ea2eedcc
  status: accepted
relations:
  - predicate: authored_by
    object: people/mei-tanaka
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/owen-fitz
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [59, 79]
        quote: mei@meridian.example
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [27, 48]
        quote: owen@meridian.example
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [143, 160]
        quote: capacity planning
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [205, 211]
        quote: Linear
---

**From:** Owen Fitzgerald <owen@meridian.example>

**To:** mei@meridian.example

**Date:** 2024-02-28T14:00:00+00:00

Hi Mei,

Following up on capacity planning. Owen Fitzgerald owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Owen Fitzgerald
