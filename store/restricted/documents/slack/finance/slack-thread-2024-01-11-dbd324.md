---
id: documents/slack/finance/slack-thread-2024-01-11-dbd324
type: Document
title: Slack thread — 2024-01-11
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/finance/2024-01-11.json
  external_id: slack/finance/2024-01-11.json
  external_version: d2ec1d19bb922966
  content_sha256: d2ec1d19bb9229668cb5f34f3e38a5b73815fe365461b69071cccf760d1e3bb6
timestamps:
  created: '2024-01-11T10:12:00Z'
  modified: '2024-01-11T10:33:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: c11bc7b4190a73e5a811f5c0c839c140
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/customer-escalation
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [23, 105]
        quote: Customer escalation is blocked until Engineering signs off on the security review.
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [129, 173]
        quote: 'Reminder: Customer escalation closes Friday.'
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [197, 241]
        quote: 'Reminder: Employee onboarding closes Friday.'
  - predicate: mentions
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [23, 105]
        quote: Customer escalation is blocked until Engineering signs off on the security review.
  - predicate: mentions
    object: tools/linear
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [266, 300]
        quote: The Linear renewal lands in April.
  - predicate: owns
    subject: people/ana-brito
    object: processes/vendor-renewal
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [301, 323]
        quote: I own that end to end.
---

**Ana Brito** (10:12): Customer escalation is blocked until Engineering signs off on the security review.

**Sam Kaur** (10:19): Reminder: Customer escalation closes Friday.

**Sam Kaur** (10:26): Reminder: Employee onboarding closes Friday.

**Ana Brito** (10:33): The Linear renewal lands in April. I own that end to end.
