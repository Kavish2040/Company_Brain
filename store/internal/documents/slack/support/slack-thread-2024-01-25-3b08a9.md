---
id: documents/slack/support/slack-thread-2024-01-25-3b08a9
type: Document
title: Slack thread — 2024-01-25
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-25.json
  external_id: slack/support/2024-01-25.json
  external_version: b4006923421ab2c0
  content_sha256: b4006923421ab2c07597d4ef6f2a25ac0086b9fad421e048412e61401ebc413e
timestamps:
  created: '2024-01-25T09:09:00Z'
  modified: '2024-01-25T09:23:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: b7e92a0d3195d5535d26094300487b1b
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [111, 123]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [199, 209]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [177, 194]
        quote: Incident response
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [48, 59]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [146, 153]
        quote: Finance
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [261, 270]
        quote: PagerDuty
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [69, 78]
        quote: Snowflake
---

**Owen Fitzgerald** (09:09): Escalating this to Engineering — it's a Snowflake integration bug, not config.

**Nadia Hassan** (09:16): Looping in Finance for the refund side of Incident response.

**Tom Whelan** (09:23): Escalating this to Engineering — it's a PagerDuty integration bug, not config.
