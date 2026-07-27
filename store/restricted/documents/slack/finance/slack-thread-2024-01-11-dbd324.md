---
id: documents/slack/finance/slack-thread-2024-01-11-dbd324
type: Document
title: Slack thread — 2024-01-11
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/finance/2024-01-11.json
  external_id: finance/2024-01-11
  external_version: rev-0
  content_sha256: d2ec1d19bb9229668cb5f34f3e38a5b73815fe365461b69071cccf760d1e3bb6
timestamps:
  created: '2024-01-11T10:12:00Z'
  modified: '2024-01-11T10:33:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 2b881d0d36649bc1ae5ca42c8105a0ab
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
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [109, 117]
        quote: Sam Kaur
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 42]
        quote: Customer escalation
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [207, 226]
        quote: Employee onboarding
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [89, 104]
        quote: security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [60, 71]
        quote: Engineering
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [270, 276]
        quote: Linear
---

**Ana Brito** (10:12): Customer escalation is blocked until Engineering signs off on the security review.

**Sam Kaur** (10:19): Reminder: Customer escalation closes Friday.

**Sam Kaur** (10:26): Reminder: Employee onboarding closes Friday.

**Ana Brito** (10:33): The Linear renewal lands in April. I own that end to end.
