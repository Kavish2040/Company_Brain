---
id: documents/docs/tools/pagerduty-111064
type: Document
title: PagerDuty
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/tools/pagerduty.md
  external_id: docs/tools/pagerduty.md
  external_version: 8ac01d6dcb8a667c
  content_sha256: 8ac01d6dcb8a667cdecca30983cd86f2db391eeaf8c17aaef28bbaa4b8d6d5ff
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: d96e0656664005fa768a0bcfdc0b9569
  status: accepted
relations:
  - predicate: owns
    object: teams/product
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [30, 56]
        quote: Owned by the Product team.
---

# PagerDuty

On-call paging.

Owned by the Product team.
