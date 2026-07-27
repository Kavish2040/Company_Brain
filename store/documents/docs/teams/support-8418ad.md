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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 073234f638e3d6b6c4cc0d1a29835948
  status: accepted
relations:
  - predicate: owns
    object: processes/customer-escalation
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [154, 195]
        quote: 'Customer escalation (owner: Dev Oyelaran)'
  - predicate: owns
    object: processes/data-request
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [198, 239]
        quote: 'Customer data request (owner: Mei Tanaka)'
---

# Support

## Members

- Dev Oyelaran — Support Lead (dev@meridian.example)
- Mei Tanaka — Support Engineer (mei@meridian.example)

## Processes owned

- Customer escalation (owner: Dev Oyelaran)
- Customer data request (owner: Mei Tanaka)
