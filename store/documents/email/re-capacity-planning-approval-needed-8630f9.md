---
id: documents/email/re-capacity-planning-approval-needed-8630f9
type: Document
title: 'Re: Capacity planning ��� approval needed'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-007.eml
  external_id: email/thread-007.eml
  external_version: c543cca4d4721d52
  content_sha256: c543cca4d4721d5201dceb59980cd34e24966763416836a994c6403ee5bd6f47
authors:
  - people/mei-tanaka
  - people/owen-fitz
timestamps:
  created: &id001 '2024-01-24T12:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 8d67ab795af1a2feff2453e75ab7eb4a
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
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [205, 214]
        quote: Snowflake
---

**From:** Owen Fitzgerald <owen@meridian.example>

**To:** mei@meridian.example

**Date:** 2024-01-24T12:00:00+00:00

Hi Mei,

Following up on capacity planning. Owen Fitzgerald owns this process, but the Snowflake step is blocked on your team.

Can you confirm by Friday?

Thanks,
Owen Fitzgerald
