---
id: documents/slack/finance/slack-thread-2024-01-16-d2e453
type: Document
title: Slack thread — 2024-01-16
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/finance/2024-01-16.json
  external_id: slack/finance/2024-01-16.json
  external_version: 849db25fa27ccb65
  content_sha256: 849db25fa27ccb65a8962f6e6cf897123875ddffcf923b42e5b8b4d47579ba1d
timestamps:
  created: '2024-01-16T14:12:00Z'
  modified: '2024-01-16T14:33:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 07df08bea5d1684035688989ee3cb045
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: Ana Brito
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [153, 161]
        quote: Sam Kaur
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [33, 50]
        quote: Capacity planning
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [275, 296]
        quote: Customer data request
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [173, 188]
        quote: Quarterly close
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [235, 250]
        quote: security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [206, 217]
        quote: Engineering
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [94, 102]
        quote: NetSuite
---

**Ana Brito** (14:12): Reminder: Capacity planning closes Friday.

**Ana Brito** (14:19): The NetSuite renewal lands in April. I own that end to end.

**Sam Kaur** (14:26): Quarterly close is blocked until Engineering signs off on the security review.

**Sam Kaur** (14:33): Customer data request is blocked until Engineering signs off on the security review.
