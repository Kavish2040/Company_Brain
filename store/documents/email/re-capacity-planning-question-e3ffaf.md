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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: d0a58d7074c92b9a9279be26adb43f50
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
  - predicate: depends_on
    object: tools/linear
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [201, 241]
        quote: the Linear step is blocked on your team.
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [118, 125]
        quote: Hi Mei,
  - predicate: owns
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [162, 195]
        quote: Owen Fitzgerald owns this process
---

**From:** Owen Fitzgerald <owen@meridian.example>

**To:** mei@meridian.example

**Date:** 2024-02-28T14:00:00+00:00

Hi Mei,

Following up on capacity planning. Owen Fitzgerald owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Owen Fitzgerald
