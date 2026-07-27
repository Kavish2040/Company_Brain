---
id: documents/slack/finance/slack-thread-2024-01-12-d0c290
type: Document
title: Slack thread — 2024-01-12
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/finance/2024-01-12.json
  external_id: slack/finance/2024-01-12.json
  external_version: 354b3a763a40bd84
  content_sha256: 354b3a763a40bd84aceef521e8a683b668f932628ed3be6bd03692004ea751d9
timestamps:
  created: '2024-01-12T12:40:00Z'
  modified: '2024-01-12T12:54:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 55ccb9850ee4f98523fc7c800b09a123
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [72, 81]
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
        span: [32, 53]
        quote: Customer data request
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [103, 118]
        quote: Quarterly close
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [168, 183]
        quote: Refund approval
---

**Sam Kaur** (12:40): Reminder: Customer data request closes Friday.

**Ana Brito** (12:47): Reminder: Quarterly close closes Friday.

**Ana Brito** (12:54): Reminder: Refund approval closes Friday.
