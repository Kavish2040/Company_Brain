---
id: documents/slack/general/slack-thread-2024-01-24-bf8d96
type: Document
title: Slack thread — 2024-01-24
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-24.json
  external_id: slack/general/2024-01-24.json
  external_version: d844f700013805ad
  content_sha256: d844f700013805ad71e537416c4dd9e9f00209a45b40cffcc1f1a542c9d922d8
timestamps:
  created: '2024-01-24T10:43:00Z'
  modified: '2024-01-24T11:04:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 906454417a057d8d1a1109dbae4ea803
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [136, 145]
        quote: Ana Brito
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [55, 66]
        quote: Priya Raman
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
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [92, 111]
        quote: Employee onboarding
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [171, 186]
        quote: Quarterly close
---

**Sam Kelly** (10:43): All-hands moved to Thursday.

**Priya Raman** (10:50): Reminder that Employee onboarding kicks off next week.

**Ana Brito** (10:57): Reminder that Quarterly close kicks off next week.

**Priya Raman** (11:04): Welcome to the team! Onboarding docs are in Drive.
