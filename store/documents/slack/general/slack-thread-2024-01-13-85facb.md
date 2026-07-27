---
id: documents/slack/general/slack-thread-2024-01-13-85facb
type: Document
title: Slack thread — 2024-01-13
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-13.json
  external_id: slack/general/2024-01-13.json
  external_version: 1c8eca18e1501f56
  content_sha256: 1c8eca18e1501f562fdef38874e2927cf5d793c67c616c1282412864602ef517
timestamps:
  created: '2024-01-13T13:03:00Z'
  modified: '2024-01-13T13:24:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 39d1b2752dc24e0b6aed4658b119888c
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [78, 87]
        quote: Ana Brito
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [153, 165]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 12]
        quote: Tom Whelan
---

**Tom Whelan** (13:03): Welcome to the team! Onboarding docs are in Drive.

**Ana Brito** (13:10): Welcome to the team! Onboarding docs are in Drive.

**Nadia Hassan** (13:17): All-hands moved to Thursday.

**Nadia Hassan** (13:24): All-hands moved to Thursday.
