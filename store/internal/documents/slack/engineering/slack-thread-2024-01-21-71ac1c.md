---
id: documents/slack/engineering/slack-thread-2024-01-21-71ac1c
type: Document
title: Slack thread — 2024-01-21
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-21.json
  external_id: slack/engineering/2024-01-21.json
  external_version: 58d30cabde65681e
  content_sha256: 58d30cabde65681eafe5dfdbf6e237d41a937d975d178b3beef62bbeb72bbb49
timestamps:
  created: '2024-01-21T12:09:00Z'
  modified: '2024-01-21T12:16:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: fa400b2cfac3e1090e9a6231d588dd8b
  status: accepted
relations:
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [85, 100]
        quote: Owen Fitzgerald
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
    object: processes/vendor-renewal
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [23, 81]
        quote: Can someone from Finance confirm the Zendesk renewal date?
  - predicate: mentions
    object: teams/finance
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 81]
        quote: Can someone from Finance confirm the Zendesk renewal date?
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [112, 170]
        quote: Can someone from Finance confirm the Datadog renewal date?
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 81]
        quote: Can someone from Finance confirm the Zendesk renewal date?
---

**Zoë Ravel** (12:09): Can someone from Finance confirm the Zendesk renewal date?

**Owen Fitzgerald** (12:16): Can someone from Finance confirm the Datadog renewal date?
