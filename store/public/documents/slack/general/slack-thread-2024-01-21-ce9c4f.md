---
id: documents/slack/general/slack-thread-2024-01-21-ce9c4f
type: Document
title: Slack thread — 2024-01-21
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-21.json
  external_id: slack/general/2024-01-21.json
  external_version: e0d93f0a099735ba
  content_sha256: e0d93f0a099735baca66b87f37ffae99938db9fff77b6a5b966bb6da835d975c
timestamps:
  created: '2024-01-21T12:29:00Z'
  modified: '2024-01-21T12:50:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 1edff6d6a0944026bf458604334c5d0c
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: Ana Brito
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [151, 163]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [229, 238]
        quote: Sam Kelly
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [264, 279]
        quote: Quarterly close
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [189, 204]
        quote: Refund approval
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [37, 51]
        quote: Vendor renewal
---

**Ana Brito** (12:29): Reminder that Vendor renewal kicks off next week.

**Ana Brito** (12:36): Welcome to the team! Onboarding docs are in Drive.

**Dev Oyelaran** (12:43): Reminder that Refund approval kicks off next week.

**Sam Kelly** (12:50): Reminder that Quarterly close kicks off next week.
