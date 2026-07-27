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
  prompt_version: claude-roster-v2
  cache_key: 0f89c9400861f656c4fa90de8c6b21bb
  status: accepted
relations:
  - predicate: owns
    subject: teams/product
    object: tools/pagerduty
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
