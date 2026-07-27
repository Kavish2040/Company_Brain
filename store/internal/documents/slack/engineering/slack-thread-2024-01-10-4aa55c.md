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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 6c0250bb49d72f5abcc4d6a8d46ffb2a
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [86, 96]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 12]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [120, 139]
        quote: Employee onboarding
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [41, 48]
        quote: Finance
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [155, 162]
        quote: Support
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [61, 68]
        quote: Datadog
---

**Tom Whelan** (12:48): Can someone from Finance confirm the Datadog renewal date?

**Mei Tanaka** (12:55): Handing the Employee onboarding ticket over to Support, they own the customer comms.
