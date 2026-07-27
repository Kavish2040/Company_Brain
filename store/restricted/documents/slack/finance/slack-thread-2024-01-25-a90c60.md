---
id: documents/slack/finance/slack-thread-2024-01-25-a90c60
type: Document
title: Slack thread — 2024-01-25
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/finance/2024-01-25.json
  external_id: slack/finance/2024-01-25.json
  external_version: 0bbe6f06439290ba
  content_sha256: 0bbe6f06439290ba30351f79139dcfefe0ce3740babde12eac8b696ebfd41ce3
timestamps:
  created: '2024-01-25T10:46:00Z'
  modified: '2024-01-25T11:07:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 8650668f2e8ca7784d2bc127c77a7b92
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [84, 93]
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
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [280, 295]
        quote: Security review
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [26, 33]
        quote: Datadog
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [109, 117]
        quote: NetSuite
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [192, 199]
        quote: Zendesk
---

**Sam Kaur** (10:46): The Datadog renewal lands in April. I own that end to end.

**Ana Brito** (10:53): The NetSuite renewal lands in April. I own that end to end.

**Sam Kaur** (11:00): The Zendesk renewal lands in April. I own that end to end.

**Sam Kaur** (11:07): Reminder: Security review closes Friday.
