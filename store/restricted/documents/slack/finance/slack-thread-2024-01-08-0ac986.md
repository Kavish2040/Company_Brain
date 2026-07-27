---
id: documents/slack/finance/slack-thread-2024-01-08-0ac986
type: Document
title: Slack thread — 2024-01-08
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/finance/2024-01-08.json
  external_id: slack/finance/2024-01-08.json
  external_version: 1c193821b6154621
  content_sha256: 1c193821b6154621c4a1f36959c7106e7d780fcea071f1aacbf5ea135ab1337d
timestamps:
  created: '2024-01-08T14:00:00Z'
  modified: '2024-01-08T14:07:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 9223ba95a1d8037bb9bc019a949b4cfe
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
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 40]
        quote: Incident response
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [87, 102]
        quote: security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [58, 69]
        quote: Engineering
---

**Ana Brito** (14:00): Incident response is blocked until Engineering signs off on the security review.

**Ana Brito** (14:07): Reminder: Security review closes Friday.
