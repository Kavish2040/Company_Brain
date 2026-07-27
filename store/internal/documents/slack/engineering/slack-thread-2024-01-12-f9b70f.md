---
id: documents/slack/engineering/slack-thread-2024-01-12-f9b70f
type: Document
title: Slack thread — 2024-01-12
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-12.json
  external_id: slack/engineering/2024-01-12.json
  external_version: d333cd2f7aac1d3b
  content_sha256: d333cd2f7aac1d3b9220d7a29ecc4a5564960cd573c88d6e5a350df38a7250ee
timestamps:
  created: '2024-01-12T11:46:00Z'
  modified: '2024-01-12T12:07:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: a0fbadf5e9410a1dff3d2c904ef2f685
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [94, 106]
        quote: Nadia Hassan
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
        span: [180, 190]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [303, 324]
        quote: Customer data request
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [353, 369]
        quote: release sign-off
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [135, 142]
        quote: Finance
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [29, 38]
        quote: PagerDuty
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [239, 248]
        quote: Snowflake
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [155, 162]
        quote: Zendesk
---

**Priya Raman** (11:46): The PagerDuty alert fired again overnight — third time this week.

**Nadia Hassan** (11:53): Can someone from Finance confirm the Zendesk renewal date?

**Tom Whelan** (12:00): Can someone from Finance confirm the Snowflake renewal date?

**Tom Whelan** (12:07): Deploy for the Customer data request change is queued behind the release sign-off.
