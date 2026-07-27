---
id: documents/slack/engineering/slack-thread-2024-01-20-0ad6d4
type: Document
title: Slack thread — 2024-01-20
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-20.json
  external_id: slack/engineering/2024-01-20.json
  external_version: a9ad0abc2edb60b7
  content_sha256: a9ad0abc2edb60b77355276f01a35e7e08e464edb1ced519e66cdd11534deee2
timestamps:
  created: '2024-01-20T09:48:00Z'
  modified: '2024-01-20T10:09:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 53e2786b4d0113805c81237589ce569c
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [199, 208]
        quote: Ana Brito
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [88, 103]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [287, 296]
        quote: Sam Kelly
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 12]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [127, 142]
        quote: Security review
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [41, 48]
        quote: Finance
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [158, 165]
        quote: Support
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [224, 231]
        quote: Datadog
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [61, 70]
        quote: PagerDuty
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [312, 321]
        quote: Snowflake
---

**Tom Whelan** (09:48): Can someone from Finance confirm the PagerDuty renewal date?

**Owen Fitzgerald** (09:55): Handing the Security review ticket over to Support, they own the customer comms.

**Ana Brito** (10:02): The Datadog alert fired again overnight — third time this week.

**Sam Kelly** (10:09): The Snowflake alert fired again overnight — third time this week.
