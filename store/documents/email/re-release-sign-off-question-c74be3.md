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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: e0006a71ca5c8a280e9b7ac3108483c5
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
  - predicate: depends_on
    object: tools/datadog
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [164, 240]
        quote: Priya Raman owns this process, but the Datadog step is blocked on your team.
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [130, 163]
        quote: Following up on release sign-off.
  - predicate: owns
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [164, 240]
        quote: Priya Raman owns this process, but the Datadog step is blocked on your team.
---

**From:** Sam Kaur <sam.kaur@meridian.example>

**To:** sam.kelly@meridian.example

**Date:** 2024-01-28T16:00:00+00:00

Hi Sam,

Following up on release sign-off. Priya Raman owns this process, but the Datadog step is blocked on your team.

Can you confirm by Friday?

Thanks,
Sam Kaur
