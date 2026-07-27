---
id: documents/slack/finance/slack-thread-2024-01-19-4ec231
type: Document
title: Slack thread — 2024-01-19
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/finance/2024-01-19.json
  external_id: finance/2024-01-19
  external_version: rev-0
  content_sha256: 8c76891ddcd217a9d8da635c43b2da24886c7342885f4a94e5155faf857de37b
timestamps:
  created: '2024-01-19T12:10:00Z'
  modified: '2024-01-19T12:24:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 62305860e7cb98e20191c14ab47da8da
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [138, 147]
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
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [169, 186]
        quote: Capacity planning
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [32, 51]
        quote: Employee onboarding
---

**Sam Kaur** (12:10): Reminder: Employee onboarding closes Friday.

**Sam Kaur** (12:17): Reminder: Employee onboarding closes Friday.

**Ana Brito** (12:24): Reminder: Capacity planning closes Friday.
