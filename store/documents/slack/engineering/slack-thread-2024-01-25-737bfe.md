---
id: documents/slack/engineering/slack-thread-2024-01-25-737bfe
type: Document
title: Slack thread — 2024-01-25
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-25.json
  external_id: slack/engineering/2024-01-25.json
  external_version: 4339bfee933a420e
  content_sha256: 4339bfee933a420e8fa5c4e7565bcc1dd3fc10b45116259da9fd84ac42952222
timestamps:
  created: '2024-01-25T12:14:00Z'
  modified: '2024-01-25T12:21:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 4e097181d4ee82b0bac9993f5ab65127
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 12]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [103, 113]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [82, 98]
        quote: release sign-off
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [39, 53]
        quote: Vendor renewal
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [129, 135]
        quote: Linear
---

**Mei Tanaka** (12:14): Deploy for the Vendor renewal change is queued behind the release sign-off.

**Tom Whelan** (12:21): The Linear alert fired again overnight — third time this week.
