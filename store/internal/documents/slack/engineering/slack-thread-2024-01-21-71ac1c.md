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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 74199cdee1abc972c447a72799f8a2b9
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
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [40, 47]
        quote: Finance
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [149, 156]
        quote: Datadog
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [60, 67]
        quote: Zendesk
---

**Zoë Ravel** (12:09): Can someone from Finance confirm the Zendesk renewal date?

**Owen Fitzgerald** (12:16): Can someone from Finance confirm the Datadog renewal date?
