---
id: documents/email/re-incident-response-question-41f894
type: Document
title: 'Re: Incident response ��� question'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-011.eml
  external_id: email/thread-011.eml
  external_version: 169b4fb5cc3a4f40
  content_sha256: 169b4fb5cc3a4f40471398f4854a7eb2d4ff3530a331d9c82826bb0935c9212d
authors:
  - people/priya-raman
  - people/sam-kaur
timestamps:
  created: &id001 '2024-01-13T11:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: daa514fe874add040f539d6e7e70308e
  status: accepted
relations:
  - predicate: authored_by
    object: people/priya-raman
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/sam-kaur
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
        span: [163, 178]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [56, 78]
        quote: priya@meridian.example
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [20, 45]
        quote: sam.kaur@meridian.example
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [144, 161]
        quote: incident response
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [206, 215]
        quote: PagerDuty
---

**From:** Sam Kaur <sam.kaur@meridian.example>

**To:** priya@meridian.example

**Date:** 2024-01-13T11:00:00+00:00

Hi Priya,

Following up on incident response. Owen Fitzgerald owns this process, but the PagerDuty step is blocked on your team.

Can you confirm by Friday?

Thanks,
Sam Kaur
