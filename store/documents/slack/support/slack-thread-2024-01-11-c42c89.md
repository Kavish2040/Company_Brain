---
id: documents/slack/support/slack-thread-2024-01-11-c42c89
type: Document
title: Slack thread — 2024-01-11
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-11.json
  external_id: slack/support/2024-01-11.json
  external_version: d657d501b66565b7
  content_sha256: d657d501b66565b76c78ad4fa35f55489f41567d3798e00bddbfb6a627b88572
timestamps:
  created: '2024-01-11T12:52:00Z'
  modified: '2024-01-11T13:06:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 187c950915ebd19f3258b0a8e9be7177
  status: accepted
relations:
  - predicate: handoff_to
    subject: people/zoe-ravel
    object: teams/engineering
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [213, 289]
        quote: Escalating this to Engineering — it's a Zendesk integration bug, not config.
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [109, 188]
        quote: This is the fourth ticket bounced back from Engineering on Employee onboarding.
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 83]
        quote: Customer is asking about the Refund approval timeline again.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [109, 188]
        quote: This is the fourth ticket bounced back from Engineering on Employee onboarding.
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [213, 289]
        quote: Escalating this to Engineering — it's a Zendesk integration bug, not config.
---

**Ana Brito** (12:52): Customer is asking about the Refund approval timeline again.

**Tom Whelan** (12:59): This is the fourth ticket bounced back from Engineering on Employee onboarding.

**Zoë Ravel** (13:06): Escalating this to Engineering — it's a Zendesk integration bug, not config.
