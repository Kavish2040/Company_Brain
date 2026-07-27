---
id: documents/slack/finance/slack-thread-2024-01-20-71ab57
type: Document
title: Slack thread — 2024-01-20
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/finance/2024-01-20.json
  external_id: finance/2024-01-20
  external_version: rev-0
  content_sha256: 682db423b5cfe9e6d57da30ed82fd9b46403ec5737c2e63649bbc8cdb81d5e33
timestamps:
  created: '2024-01-20T13:33:00Z'
  modified: '2024-01-20T13:54:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 39d919a63289745448f28923b58408c0
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
        span: [197, 205]
        quote: Sam Kaur
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [33, 48]
        quote: Quarterly close
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [162, 178]
        quote: Release sign-off
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [278, 293]
        quote: security review
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [98, 112]
        quote: Vendor renewal
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [249, 260]
        quote: Engineering
---

**Ana Brito** (13:33): Reminder: Quarterly close closes Friday.

**Ana Brito** (13:40): Reminder: Vendor renewal closes Friday.

**Ana Brito** (13:47): Reminder: Release sign-off closes Friday.

**Sam Kaur** (13:54): Vendor renewal is blocked until Engineering signs off on the security review.
