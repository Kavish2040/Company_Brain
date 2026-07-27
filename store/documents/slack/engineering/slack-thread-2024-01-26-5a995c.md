---
id: documents/slack/engineering/slack-thread-2024-01-26-5a995c
type: Document
title: Slack thread — 2024-01-26
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-26.json
  external_id: slack/engineering/2024-01-26.json
  external_version: 18faa3046211eff3
  content_sha256: 18faa3046211eff3c0d46c7cd3e47c95e1a7fcf6b331111e5304807ef84f9af1
timestamps:
  created: '2024-01-26T13:15:00Z'
  modified: '2024-01-26T13:36:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 6a0bf8ac770a4d83dbeb4f5603804946
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [92, 104]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [272, 283]
        quote: Priya Raman
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [185, 194]
        quote: Sam Kelly
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: Zoë Ravel
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [312, 319]
        quote: Finance
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [332, 339]
        quote: Datadog
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [210, 216]
        quote: Linear
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [27, 36]
        quote: PagerDuty
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [120, 129]
        quote: Snowflake
---

**Zoë Ravel** (13:15): The PagerDuty alert fired again overnight — third time this week.

**Dev Oyelaran** (13:22): The Snowflake alert fired again overnight — third time this week.

**Sam Kelly** (13:29): The Linear alert fired again overnight — third time this week.

**Priya Raman** (13:36): Can someone from Finance confirm the Datadog renewal date?
