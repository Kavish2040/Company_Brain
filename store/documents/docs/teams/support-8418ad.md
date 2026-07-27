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
  prompt_version: claude-roster-v2
  cache_key: c4c500b0e929114ce0eda094feb2e6a3
  status: accepted
relations:
  - predicate: owns
    subject: people/dev-oyelaran
    object: processes/customer-escalation
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [154, 195]
        quote: 'Customer escalation (owner: Dev Oyelaran)'
  - predicate: owns
    subject: people/mei-tanaka
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
