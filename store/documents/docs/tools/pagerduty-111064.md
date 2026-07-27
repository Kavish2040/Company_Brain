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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 28ac84f3713333a1eca9bb34732aa246
  status: accepted
relations:
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [43, 50]
        quote: Product
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: PagerDuty
---

# PagerDuty

On-call paging.

Owned by the Product team.
