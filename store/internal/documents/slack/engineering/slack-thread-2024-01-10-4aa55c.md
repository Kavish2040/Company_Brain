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
  prompt_version: claude-roster-v2
  cache_key: 256f23f567e7022708abf199a9d81022
  status: accepted
relations:
  - predicate: mentions
    object: teams/finance
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [24, 82]
        quote: Can someone from Finance confirm the Datadog renewal date?
  - predicate: mentions
    object: tools/datadog
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [24, 82]
        quote: Can someone from Finance confirm the Datadog renewal date?
---

**Tom Whelan** (12:48): Can someone from Finance confirm the Datadog renewal date?

**Mei Tanaka** (12:55): Handing the Employee onboarding ticket over to Support, they own the customer comms.
