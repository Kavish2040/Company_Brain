---
id: documents/slack/engineering/slack-thread-2024-01-13-d4fca0
type: Document
title: Slack thread — 2024-01-13
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-13.json
  external_id: slack/engineering/2024-01-13.json
  external_version: 16633adbebc455f1
  content_sha256: 16633adbebc455f1675256f34a6d03ed4bbf4b38646a07d8587f463ae42b5e17
timestamps:
  created: '2024-01-13T14:19:00Z'
  modified: '2024-01-13T14:40:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: e63f2dea19efa184cecb7453aba4f67f
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [108, 120]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [285, 300]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [201, 209]
        quote: Sam Kaur
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: Sam Kelly
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [327, 348]
        quote: Customer data request
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [35, 51]
        quote: Release sign-off
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [238, 245]
        quote: Finance
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [67, 74]
        quote: Support
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [136, 145]
        quote: PagerDuty
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [258, 267]
        quote: Snowflake
---

**Sam Kelly** (14:19): Handing the Release sign-off ticket over to Support, they own the customer comms.

**Nadia Hassan** (14:26): The PagerDuty alert fired again overnight — third time this week.

**Sam Kaur** (14:33): Can someone from Finance confirm the Snowflake renewal date?

**Owen Fitzgerald** (14:40): Deploy for the Customer data request change is queued behind the release sign-off.
