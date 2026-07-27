---
id: documents/email/re-release-sign-off-question-c74be3
type: Document
title: 'Re: Release sign-off ��� question'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-020.eml
  external_id: email/thread-020.eml
  external_version: 53a86ab968f882a6
  content_sha256: 53a86ab968f882a64df6e60c780666f855fb8bf8eb580f164c58183ebafdaf68
authors:
  - people/sam-kaur
  - people/sam-kelly
timestamps:
  created: &id001 '2024-01-28T16:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: a273b37509005c9c5d096d8f2f7848b0
  status: accepted
relations:
  - predicate: authored_by
    object: people/sam-kaur
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/sam-kelly
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [164, 175]
        quote: Priya Raman
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
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [56, 82]
        quote: sam.kelly@meridian.example
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [146, 162]
        quote: release sign-off
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

**From:** Sam Kaur <sam.kaur@meridian.example>

**To:** sam.kelly@meridian.example

**Date:** 2024-01-28T16:00:00+00:00

Hi Sam,

Following up on release sign-off. Priya Raman owns this process, but the Datadog step is blocked on your team.

Can you confirm by Friday?

Thanks,
Sam Kaur
