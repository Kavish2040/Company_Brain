---
id: documents/email/re-incident-response-approval-needed-779a39
type: Document
title: 'Re: Incident response ��� approval needed'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-006.eml
  external_id: email/thread-006.eml
  external_version: ba419d96fc215845
  content_sha256: ba419d96fc21584529d4530bb71422b508ec8eba163bf239720be10046e24589
authors:
  - people/nadia-hassan
  - people/sam-kelly
timestamps:
  created: &id001 '2024-03-07T12:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 7e2918565fb6d0df0605dd51afcc2300
  status: accepted
relations:
  - predicate: authored_by
    object: people/nadia-hassan
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/sam-kelly
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
        span: [58, 80]
        quote: nadia@meridian.example
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [165, 180]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [21, 47]
        quote: sam.kelly@meridian.example
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [146, 163]
        quote: incident response
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [208, 217]
        quote: PagerDuty
---

**From:** Sam Kelly <sam.kelly@meridian.example>

**To:** nadia@meridian.example

**Date:** 2024-03-07T12:00:00+00:00

Hi Nadia,

Following up on incident response. Owen Fitzgerald owns this process, but the PagerDuty step is blocked on your team.

Can you confirm by Friday?

Thanks,
Sam Kelly
