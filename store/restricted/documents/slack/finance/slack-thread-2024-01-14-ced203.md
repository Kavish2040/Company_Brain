---
id: documents/slack/finance/slack-thread-2024-01-14-ced203
type: Document
title: Slack thread — 2024-01-14
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/finance/2024-01-14.json
  external_id: finance/2024-01-14
  external_version: rev-0
  content_sha256: a94689329ea31ec73d113fd65973ab0023597361048358beac198f4ca8d9b1eb
timestamps:
  created: '2024-01-14T13:12:00Z'
  modified: '2024-01-14T13:26:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 26abd0aac94e2076fe3ba16cbcb2b2bf
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [86, 95]
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
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [209, 230]
        quote: Customer data request
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [107, 122]
        quote: Quarterly close
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [169, 184]
        quote: security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [140, 151]
        quote: Engineering
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [26, 35]
        quote: Snowflake
---

**Sam Kaur** (13:12): The Snowflake renewal lands in April. I own that end to end.

**Ana Brito** (13:19): Quarterly close is blocked until Engineering signs off on the security review.

**Sam Kaur** (13:26): Customer data request is blocked until Engineering signs off on the security review.
