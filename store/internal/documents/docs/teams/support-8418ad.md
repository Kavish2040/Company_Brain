---
id: documents/docs/teams/support-8418ad
type: Document
title: Support
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/teams/support.md
  external_id: docs/teams/support.md
  external_version: 81c01a4b80ff5475
  content_sha256: 81c01a4b80ff5475a13a2e16b03bcf838a32c6c2015e70f5743ab9ee330aef87
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 0b610993103ee2d495e66d869476ee50
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [54, 74]
        quote: dev@meridian.example
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [109, 129]
        quote: mei@meridian.example
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [154, 173]
        quote: Customer escalation
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [198, 219]
        quote: Customer data request
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 9]
        quote: Support
---

# Support

## Members

- Dev Oyelaran — Support Lead (dev@meridian.example)
- Mei Tanaka — Support Engineer (mei@meridian.example)

## Processes owned

- Customer escalation (owner: Dev Oyelaran)
- Customer data request (owner: Mei Tanaka)
