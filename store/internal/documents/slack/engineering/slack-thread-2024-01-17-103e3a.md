---
id: documents/slack/engineering/slack-thread-2024-01-17-103e3a
type: Document
title: Slack thread — 2024-01-17
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: slack
  uri: file://corpus/slack/engineering/2024-01-17.json
  external_id: engineering/2024-01-17
  external_version: rev-0
  content_sha256: 7a0d24ae4ce95e6fdb660a515804767b74edcd1651a1fdb8d4c6ca9c699c4815
timestamps:
  created: '2024-01-17T09:29:00Z'
  modified: '2024-01-17T09:36:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 9f63423d03a2b240be7f488331ec69a9
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 13]
        quote: Priya Raman
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [121, 140]
        quote: Employee onboarding
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [42, 49]
        quote: Finance
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [156, 163]
        quote: Support
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [62, 68]
        quote: Linear
---

**Priya Raman** (09:29): Can someone from Finance confirm the Linear renewal date?

**Priya Raman** (09:36): Handing the Employee onboarding ticket over to Support, they own the customer comms.
