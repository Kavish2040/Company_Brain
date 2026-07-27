---
id: documents/slack/engineering/slack-thread-2024-01-17-103e3a
type: Document
title: Slack thread — 2024-01-17
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-17.json
  external_id: slack/engineering/2024-01-17.json
  external_version: 7a0d24ae4ce95e6f
  content_sha256: 7a0d24ae4ce95e6fdb660a515804767b74edcd1651a1fdb8d4c6ca9c699c4815
timestamps:
  created: '2024-01-17T09:29:00Z'
  modified: '2024-01-17T09:36:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 977f154769b4e9a7e7cbf85843b8fa3a
  status: accepted
relations:
  - predicate: handoff_to
    object: teams/support
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [109, 193]
        quote: Handing the Employee onboarding ticket over to Support, they own the customer comms.
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [109, 193]
        quote: Handing the Employee onboarding ticket over to Support, they own the customer comms.
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.55
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [25, 82]
        quote: Can someone from Finance confirm the Linear renewal date?
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [25, 82]
        quote: Can someone from Finance confirm the Linear renewal date?
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [25, 82]
        quote: Can someone from Finance confirm the Linear renewal date?
---

**Priya Raman** (09:29): Can someone from Finance confirm the Linear renewal date?

**Priya Raman** (09:36): Handing the Employee onboarding ticket over to Support, they own the customer comms.
