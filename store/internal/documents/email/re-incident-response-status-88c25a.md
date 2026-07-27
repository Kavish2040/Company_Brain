---
id: documents/email/re-incident-response-status-88c25a
type: Document
title: 'Re: Incident response ��� status'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-010.eml
  external_id: email/thread-010.eml
  external_version: e08e68feb924d6a9
  content_sha256: e08e68feb924d6a9e0f40fb7e7248a13c95ca0f01bf3fa580205033c86716b3d
authors:
  - people/mei-tanaka
  - people/sam-kaur
timestamps:
  created: &id001 '2024-01-13T10:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 4f0c2d0099acb11226e155fbd446f246
  status: accepted
relations:
  - predicate: authored_by
    object: people/mei-tanaka
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/sam-kaur
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
        span: [22, 42]
        quote: mei@meridian.example
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [161, 176]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [53, 78]
        quote: sam.kaur@meridian.example
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [142, 159]
        quote: incident response
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [204, 213]
        quote: PagerDuty
---

**From:** Mei Tanaka <mei@meridian.example>

**To:** sam.kaur@meridian.example

**Date:** 2024-01-13T10:00:00+00:00

Hi Sam,

Following up on incident response. Owen Fitzgerald owns this process, but the PagerDuty step is blocked on your team.

Can you confirm by Friday?

Thanks,
Mei Tanaka
