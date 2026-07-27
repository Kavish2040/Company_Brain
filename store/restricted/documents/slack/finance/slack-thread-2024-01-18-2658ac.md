---
id: documents/slack/finance/slack-thread-2024-01-18-2658ac
type: Document
title: Slack thread — 2024-01-18
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/finance/2024-01-18.json
  external_id: finance/2024-01-18
  external_version: rev-0
  content_sha256: b3dedc37213af302404d7d8efc60cf647fb5ebfea8ba444c050f6e55f99858ab
timestamps:
  created: '2024-01-18T14:32:00Z'
  modified: '2024-01-18T14:53:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 226c761972b6e611d397ab4847cae41b
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [148, 157]
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
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [232, 247]
        quote: Quarterly close
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [32, 47]
        quote: Refund approval
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [294, 309]
        quote: security review
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [179, 193]
        quote: Vendor renewal
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [265, 276]
        quote: Engineering
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [90, 97]
        quote: Zendesk
---

**Sam Kaur** (14:32): Reminder: Refund approval closes Friday.

**Sam Kaur** (14:39): The Zendesk renewal lands in April. I own that end to end.

**Ana Brito** (14:46): Reminder: Vendor renewal closes Friday.

**Sam Kaur** (14:53): Quarterly close is blocked until Engineering signs off on the security review.
