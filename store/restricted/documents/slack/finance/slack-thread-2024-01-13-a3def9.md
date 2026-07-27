---
id: documents/slack/finance/slack-thread-2024-01-13-a3def9
type: Document
title: Slack thread — 2024-01-13
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/finance/2024-01-13.json
  external_id: slack/finance/2024-01-13.json
  external_version: a57c3d2269c981da
  content_sha256: a57c3d2269c981daa30d82d72a0bc56dff966f77476b2c5211bf4a27bdec2c98
timestamps:
  created: '2024-01-13T10:44:00Z'
  modified: '2024-01-13T11:05:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 0f02057abf19aaabadfc985beba2b9be
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [298, 307]
        quote: Ana Brito
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 10]
        quote: Sam Kaur
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [104, 123]
        quote: Customer escalation
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [210, 231]
        quote: Customer data request
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [329, 345]
        quote: Release sign-off
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [170, 185]
        quote: security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [141, 152]
        quote: Engineering
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [26, 33]
        quote: Zendesk
---

**Sam Kaur** (10:44): The Zendesk renewal lands in April. I own that end to end.

**Sam Kaur** (10:51): Customer escalation is blocked until Engineering signs off on the security review.

**Sam Kaur** (10:58): Customer data request is blocked until Engineering signs off on the security review.

**Ana Brito** (11:05): Reminder: Release sign-off closes Friday.
