---
id: documents/slack/support/slack-thread-2024-01-19-7d438f
type: Document
title: Slack thread — 2024-01-19
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-19.json
  external_id: slack/support/2024-01-19.json
  external_version: 305a1d6823e2ae31
  content_sha256: 305a1d6823e2ae3109eee8fa4e02f735d05ffd11a035912bd71bad58def1df21
timestamps:
  created: '2024-01-19T12:22:00Z'
  modified: '2024-01-19T12:36:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 448b87857c0072a53e93d3e315b762a9
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [91, 100]
        quote: Ana Brito
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [178, 190]
        quote: Nadia Hassan
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
        span: [65, 86]
        quote: Customer data request
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [154, 173]
        quote: Employee onboarding
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [246, 257]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [34, 41]
        quote: Finance
---

**Zoë Ravel** (12:22): Looping in Finance for the refund side of Customer data request.

**Ana Brito** (12:29): Looping in Finance for the refund side of Employee onboarding.

**Nadia Hassan** (12:36): This is the fourth ticket bounced back from Engineering on Customer data request.
