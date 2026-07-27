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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 0faa50e6065a31a5df51e20e1312cf8a
  status: accepted
relations:
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [20, 27]
        quote: support
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 9]
        quote: Zendesk
---

# Zendesk

Customer support ticketing.

Owned by the Support team.
