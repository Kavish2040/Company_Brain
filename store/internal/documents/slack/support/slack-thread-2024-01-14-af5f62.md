---
id: documents/slack/support/slack-thread-2024-01-14-af5f62
type: Document
title: Slack thread — 2024-01-14
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-14.json
  external_id: slack/support/2024-01-14.json
  external_version: 9043fa4818d3beab
  content_sha256: 9043fa4818d3beab343642d2f57600cee067dd933a028136261e910e8ba88f13
timestamps:
  created: '2024-01-14T09:28:00Z'
  modified: '2024-01-14T09:42:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: db45b17ba8f91f73edb75582f86a08ec
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [88, 100]
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
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [178, 187]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [141, 158]
        quote: Capacity planning
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [241, 256]
        quote: Quarterly close
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [67, 83]
        quote: Release sign-off
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [36, 43]
        quote: Finance
---

**Priya Raman** (09:28): Looping in Finance for the refund side of Release sign-off.

**Nadia Hassan** (09:35): Customer is asking about the Capacity planning timeline again.

**Zoë Ravel** (09:42): Looping in Finance for the refund side of Quarterly close.
