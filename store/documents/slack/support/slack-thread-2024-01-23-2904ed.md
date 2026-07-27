---
id: documents/slack/support/slack-thread-2024-01-23-2904ed
type: Document
title: Slack thread — 2024-01-23
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-23.json
  external_id: slack/support/2024-01-23.json
  external_version: 72ef3c706e9ba354
  content_sha256: 72ef3c706e9ba354535e0dd1258f9bee1fefccc225de1fc5818a50fae33e777c
timestamps:
  created: '2024-01-23T09:35:00Z'
  modified: '2024-01-23T09:56:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 428ebf157897a01296493290b14c503a
  status: accepted
relations:
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [310, 318]
        quote: Sam Kaur
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [105, 115]
        quote: Tom Whelan
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
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [290, 305]
        quote: Refund approval
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [389, 403]
        quote: Vendor renewal
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [42, 53]
        quote: Engineering
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [63, 72]
        quote: PagerDuty
---

**Zoë Ravel** (09:35): Escalating this to Engineering — it's a PagerDuty integration bug, not config.

**Tom Whelan** (09:42): Escalating this to Engineering — it's a PagerDuty integration bug, not config.

**Tom Whelan** (09:49): This is the fourth ticket bounced back from Engineering on Refund approval.

**Sam Kaur** (09:56): This is the fourth ticket bounced back from Engineering on Vendor renewal.
