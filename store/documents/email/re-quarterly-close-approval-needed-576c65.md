---
id: documents/email/re-quarterly-close-approval-needed-576c65
type: Document
title: 'Re: Quarterly close ��� approval needed'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-025.eml
  external_id: email/thread-025.eml
  external_version: 7e11d96f3a6f0857
  content_sha256: 7e11d96f3a6f08577d74986b7608d3b623f4c0ad13deae5cc6f3f01983e8a322
authors:
  - people/dev-oyelaran
  - people/sam-kaur
timestamps:
  created: &id001 '2024-02-19T13:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 50d8569df89c59b8693b49c9102d71c3
  status: accepted
relations:
  - predicate: authored_by
    object: people/dev-oyelaran
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/sam-kaur
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
        span: [157, 166]
        quote: Ana Brito
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [56, 76]
        quote: dev@meridian.example
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
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [140, 155]
        quote: quarterly close
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [194, 203]
        quote: Snowflake
---

**From:** Sam Kaur <sam.kaur@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-02-19T13:00:00+00:00

Hi Dev,

Following up on quarterly close. Ana Brito owns this process, but the Snowflake step is blocked on your team.

Can you confirm by Friday?

Thanks,
Sam Kaur
