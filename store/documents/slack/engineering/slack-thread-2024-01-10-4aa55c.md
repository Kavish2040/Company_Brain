---
id: documents/slack/engineering/slack-thread-2024-01-10-4aa55c
type: Document
title: Slack thread — 2024-01-10
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-10.json
  external_id: slack/engineering/2024-01-10.json
  external_version: f54481c37cd14b04
  content_sha256: f54481c37cd14b040ea540492e4f862049742e740c900fc93f385876acdf7c27
timestamps:
  created: '2024-01-10T12:48:00Z'
  modified: '2024-01-10T12:55:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 49dcdf013352c6b8cceecbfa4497d894
  status: accepted
relations:
  - predicate: handoff_to
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [108, 192]
        quote: Handing the Employee onboarding ticket over to Support, they own the customer comms.
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [108, 192]
        quote: Handing the Employee onboarding ticket over to Support, they own the customer comms.
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [24, 82]
        quote: Can someone from Finance confirm the Datadog renewal date?
  - predicate: mentions
    object: teams/finance
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [24, 82]
        quote: Can someone from Finance confirm the Datadog renewal date?
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [24, 82]
        quote: Can someone from Finance confirm the Datadog renewal date?
  - predicate: owns
    object: processes/onboarding
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [164, 191]
        quote: they own the customer comms
---

**Tom Whelan** (12:48): Can someone from Finance confirm the Datadog renewal date?

**Mei Tanaka** (12:55): Handing the Employee onboarding ticket over to Support, they own the customer comms.
