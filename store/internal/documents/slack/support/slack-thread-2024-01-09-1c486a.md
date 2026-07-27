---
id: documents/slack/support/slack-thread-2024-01-09-1c486a
type: Document
title: Slack thread — 2024-01-09
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: slack
  uri: file://corpus/slack/support/2024-01-09.json
  external_id: support/2024-01-09
  external_version: rev-0
  content_sha256: 78c156ad9b3d48499cdd0c87e6bf89460f154a12aeb7af9704a1b9a06f199b3e
timestamps:
  created: '2024-01-09T13:07:00Z'
  modified: '2024-01-09T13:14:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 75dbb1b2e333334d318d8fc1e984df46
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [86, 98]
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
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [139, 156]
        quote: Capacity planning
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [66, 81]
        quote: Refund approval
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [35, 42]
        quote: Finance
---

**Tom Whelan** (13:07): Looping in Finance for the refund side of Refund approval.

**Nadia Hassan** (13:14): Customer is asking about the Capacity planning timeline again.
