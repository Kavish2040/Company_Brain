---
id: documents/email/re-customer-escalation-approval-needed-38f2c0
type: Document
title: 'Re: Customer escalation ��� approval needed'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-024.eml
  external_id: email/thread-024.eml
  external_version: b397572210b890d6
  content_sha256: b397572210b890d68b64f013317fcc7794f91e9fc6e266dd07d64389d460a2ae
authors:
  - people/dev-oyelaran
timestamps:
  created: &id001 '2024-02-27T13:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: b0fb9b719bb9326828348a5ce9495093
  status: accepted
relations:
  - predicate: authored_by
    object: people/dev-oyelaran
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [24, 44]
        quote: dev@meridian.example
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [139, 158]
        quote: customer escalation
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [200, 207]
        quote: Datadog
---

**From:** Dev Oyelaran <dev@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-02-27T13:00:00+00:00

Hi Dev,

Following up on customer escalation. Dev Oyelaran owns this process, but the Datadog step is blocked on your team.

Can you confirm by Friday?

Thanks,
Dev Oyelaran
