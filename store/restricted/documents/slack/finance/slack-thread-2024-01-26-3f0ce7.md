---
id: documents/slack/finance/slack-thread-2024-01-26-3f0ce7
type: Document
title: Slack thread — 2024-01-26
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/finance/2024-01-26.json
  external_id: finance/2024-01-26
  external_version: rev-0
  content_sha256: 63d7b88cd9ae24be5f314cd007edbb0ffa1941a15d8e4718cb9edbc16f75ffa4
timestamps:
  created: '2024-01-26T09:54:00Z'
  modified: '2024-01-26T10:15:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: a4279bf65dd74e55793664027e175aa8
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [208, 217]
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
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [229, 248]
        quote: Customer escalation
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [168, 189]
        quote: Customer data request
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [32, 51]
        quote: Employee onboarding
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [295, 310]
        quote: security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [266, 277]
        quote: Engineering
---

**Sam Kaur** (09:54): Reminder: Employee onboarding closes Friday.

**Sam Kaur** (10:01): Reminder: Employee onboarding closes Friday.

**Sam Kaur** (10:08): Reminder: Customer data request closes Friday.

**Ana Brito** (10:15): Customer escalation is blocked until Engineering signs off on the security review.
