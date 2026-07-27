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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: c7e65ea4cb3608e38d09199dd8b19797
  status: accepted
relations:
  - predicate: handoff_to
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [29, 107]
        quote: Escalating this to Engineering — it's a Snowflake integration bug, not config.
  - predicate: handoff_to
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [135, 195]
        quote: Looping in Finance for the refund side of Incident response.
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [135, 195]
        quote: Looping in Finance for the refund side of Incident response.
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [254, 299]
        quote: it's a PagerDuty integration bug, not config.
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [62, 107]
        quote: it's a Snowflake integration bug, not config.
---

**Owen Fitzgerald** (09:09): Escalating this to Engineering — it's a Snowflake integration bug, not config.

**Nadia Hassan** (09:16): Looping in Finance for the refund side of Incident response.

**Tom Whelan** (09:23): Escalating this to Engineering — it's a PagerDuty integration bug, not config.
