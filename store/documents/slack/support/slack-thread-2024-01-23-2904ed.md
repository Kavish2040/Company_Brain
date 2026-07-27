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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: fe5f17c9294c320ca874901fd6f023df
  status: accepted
relations:
  - predicate: handoff_to
    subject: people/zoe-ravel
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [23, 101]
        quote: Escalating this to Engineering — it's a PagerDuty integration bug, not config.
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [231, 306]
        quote: This is the fourth ticket bounced back from Engineering on Refund approval.
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [330, 404]
        quote: This is the fourth ticket bounced back from Engineering on Vendor renewal.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [231, 306]
        quote: This is the fourth ticket bounced back from Engineering on Refund approval.
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [56, 100]
        quote: it's a PagerDuty integration bug, not config
---

**Zoë Ravel** (09:35): Escalating this to Engineering — it's a PagerDuty integration bug, not config.

**Tom Whelan** (09:42): Escalating this to Engineering — it's a PagerDuty integration bug, not config.

**Tom Whelan** (09:49): This is the fourth ticket bounced back from Engineering on Refund approval.

**Sam Kaur** (09:56): This is the fourth ticket bounced back from Engineering on Vendor renewal.
