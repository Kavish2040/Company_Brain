---
id: documents/slack/support/slack-thread-2024-01-17-a9c8b3
type: Document
title: Slack thread — 2024-01-17
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-17.json
  external_id: slack/support/2024-01-17.json
  external_version: 6686d7f84861ab0e
  content_sha256: 6686d7f84861ab0e11a9a20ecee91735db8fe198caeab8099334abee623e15cc
timestamps:
  created: '2024-01-17T13:46:00Z'
  modified: '2024-01-17T13:53:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: d988cd4c8d4588c5c90085594996a464
  status: accepted
relations:
  - predicate: mentions
    object: processes/data-request
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [128, 194]
        quote: Customer is asking about the Customer data request timeline again.
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [23, 102]
        quote: This is the fourth ticket bounced back from Engineering on Employee onboarding.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [23, 102]
        quote: This is the fourth ticket bounced back from Engineering on Employee onboarding.
---

**Zoë Ravel** (13:46): This is the fourth ticket bounced back from Engineering on Employee onboarding.

**Mei Tanaka** (13:53): Customer is asking about the Customer data request timeline again.
