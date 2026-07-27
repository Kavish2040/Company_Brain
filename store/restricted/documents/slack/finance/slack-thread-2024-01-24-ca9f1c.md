---
id: documents/slack/finance/slack-thread-2024-01-24-ca9f1c
type: Document
title: Slack thread — 2024-01-24
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/finance/2024-01-24.json
  external_id: finance/2024-01-24
  external_version: rev-0
  content_sha256: acc8402283f905324c09616b945bdf0abdc1274cba587be3109c600b3fe67401
timestamps:
  created: '2024-01-24T13:25:00Z'
  modified: '2024-01-24T13:46:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: f6c360aa6aec33783c57955d27ea4b87
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [104, 113]
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
        span: [301, 322]
        quote: Customer data request
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [22, 37]
        quote: Refund approval
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [84, 99]
        quote: security review
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [135, 149]
        quote: Vendor renewal
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [55, 66]
        quote: Engineering
---

**Sam Kaur** (13:25): Refund approval is blocked until Engineering signs off on the security review.

**Ana Brito** (13:32): Reminder: Vendor renewal closes Friday.

**Ana Brito** (13:39): Security review is blocked until Engineering signs off on the security review.

**Sam Kaur** (13:46): Reminder: Customer data request closes Friday.
