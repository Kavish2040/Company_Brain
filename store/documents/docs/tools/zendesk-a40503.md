---
id: documents/docs/tools/zendesk-a40503
type: Document
title: Zendesk
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/tools/zendesk.md
  external_id: docs/tools/zendesk.md
  external_version: d22ad788a69ae5cf
  content_sha256: d22ad788a69ae5cf04b1dd5f41b37dd0d05ec5185cdf77ff7bf5277d6ce3b927
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 99e0a64559b6dc1ef841d227764ec400
  status: accepted
relations:
  - predicate: owns
    object: teams/support
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [40, 66]
        quote: Owned by the Support team.
---

# Zendesk

Customer support ticketing.

Owned by the Support team.
