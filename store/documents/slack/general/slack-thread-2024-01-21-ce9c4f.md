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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 78e1d61dcb2276945afa2162ca611042
  status: accepted
relations:
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [118, 147]
        quote: Onboarding docs are in Drive.
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [250, 300]
        quote: Reminder that Quarterly close kicks off next week.
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [175, 225]
        quote: Reminder that Refund approval kicks off next week.
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 72]
        quote: Reminder that Vendor renewal kicks off next week.
---

**Ana Brito** (12:29): Reminder that Vendor renewal kicks off next week.

**Ana Brito** (12:36): Welcome to the team! Onboarding docs are in Drive.

**Dev Oyelaran** (12:43): Reminder that Refund approval kicks off next week.

**Sam Kelly** (12:50): Reminder that Quarterly close kicks off next week.
