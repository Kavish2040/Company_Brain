---
id: documents/slack/support/slack-thread-2024-01-17-a9c8b3
type: Document
title: Slack thread — 2024-01-17
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: slack
  uri: file://corpus/slack/support/2024-01-17.json
  external_id: support/2024-01-17
  external_version: rev-0
  content_sha256: 6686d7f84861ab0e11a9a20ecee91735db8fe198caeab8099334abee623e15cc
timestamps:
  created: '2024-01-17T13:46:00Z'
  modified: '2024-01-17T13:53:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 8f3fbe3df0a6918b23169d89596b3a8f
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [106, 116]
        quote: Mei Tanaka
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
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [157, 178]
        quote: Customer data request
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [82, 101]
        quote: Employee onboarding
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [67, 78]
        quote: Engineering
---

**Zoë Ravel** (13:46): This is the fourth ticket bounced back from Engineering on Employee onboarding.

**Mei Tanaka** (13:53): Customer is asking about the Customer data request timeline again.
