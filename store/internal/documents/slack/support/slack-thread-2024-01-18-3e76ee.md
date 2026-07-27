---
id: documents/slack/support/slack-thread-2024-01-18-3e76ee
type: Document
title: Slack thread — 2024-01-18
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: slack
  uri: file://corpus/slack/support/2024-01-18.json
  external_id: support/2024-01-18
  external_version: rev-0
  content_sha256: 651634bca3947ecd0b0e1b09675d20fb6c7168342008a3b8d34be36b46704add
timestamps:
  created: '2024-01-18T14:51:00Z'
  modified: '2024-01-18T15:05:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 0f0f5dd47c31e5482120e457e527e373
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 12]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [88, 97]
        quote: Sam Kelly
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [173, 183]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [66, 83]
        quote: Capacity planning
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [138, 153]
        quote: Quarterly close
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [239, 250]
        quote: Engineering
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

**Mei Tanaka** (14:51): Looping in Finance for the refund side of Capacity planning.

**Sam Kelly** (14:58): Customer is asking about the Quarterly close timeline again.

**Tom Whelan** (15:05): This is the fourth ticket bounced back from Engineering on Capacity planning.
