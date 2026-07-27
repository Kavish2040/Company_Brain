---
id: documents/slack/engineering/slack-thread-2024-01-14-fada26
type: Document
title: Slack thread — 2024-01-14
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-14.json
  external_id: slack/engineering/2024-01-14.json
  external_version: 336147d8ebcbda65
  content_sha256: 336147d8ebcbda6574135429c4c33a92dd5746ad0670dece0fbb740a7ab5baa2
timestamps:
  created: '2024-01-14T11:03:00Z'
  modified: '2024-01-14T11:10:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 1a355f45557f7c3ad858379bdacaee46
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
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [105, 115]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [139, 160]
        quote: Customer data request
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [84, 100]
        quote: release sign-off
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [40, 55]
        quote: Security review
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [176, 183]
        quote: Support
---

**Priya Raman** (11:03): Deploy for the Security review change is queued behind the release sign-off.

**Tom Whelan** (11:10): Handing the Customer data request ticket over to Support, they own the customer comms.
