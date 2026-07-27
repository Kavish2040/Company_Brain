---
id: documents/slack/finance/slack-thread-2024-01-10-1e1b31
type: Document
title: Slack thread — 2024-01-10
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/finance/2024-01-10.json
  external_id: finance/2024-01-10
  external_version: rev-0
  content_sha256: a953dfb5ee58c2faf42d749f26109711eca2dc4cd0037b43f123596c33dc6a41
timestamps:
  created: '2024-01-10T09:37:00Z'
  modified: '2024-01-10T09:58:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: c0f8626bfd6e85ccda78b8dfb7e7197a
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
        span: [239, 247]
        quote: Sam Kaur
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [33, 52]
        quote: Customer escalation
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [96, 103]
        quote: Datadog
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [179, 188]
        quote: PagerDuty
---

**Ana Brito** (09:37): Reminder: Customer escalation closes Friday.

**Ana Brito** (09:44): The Datadog renewal lands in April. I own that end to end.

**Ana Brito** (09:51): The PagerDuty renewal lands in April. I own that end to end.

**Sam Kaur** (09:58): The PagerDuty renewal lands in April. I own that end to end.
