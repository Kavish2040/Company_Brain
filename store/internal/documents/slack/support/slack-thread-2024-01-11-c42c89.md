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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 1b4aab503e1d9b209664865e613a4024
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
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [87, 97]
        quote: Tom Whelan
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [192, 201]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [168, 187]
        quote: Employee onboarding
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [52, 67]
        quote: Refund approval
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [153, 164]
        quote: Engineering
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [253, 260]
        quote: Zendesk
---

**Ana Brito** (12:52): Customer is asking about the Refund approval timeline again.

**Tom Whelan** (12:59): This is the fourth ticket bounced back from Engineering on Employee onboarding.

**Zoë Ravel** (13:06): Escalating this to Engineering — it's a Zendesk integration bug, not config.
