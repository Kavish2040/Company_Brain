---
id: documents/docs/teams/product-451e0b
type: Document
title: Product
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/teams/product.md
  external_id: docs/teams/product.md
  external_version: 30358f63e96de066
  content_sha256: 30358f63e96de0661039f45d508b274b10b18afa5af9bd1b88e15e217c79a6ca
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 2312a027be652a07e19913f1dafdbc86
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [97, 119]
        quote: nadia@meridian.example
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [54, 74]
        quote: zoe@meridian.example
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [144, 163]
        quote: Employee onboarding
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 9]
        quote: Product
---

# Product

## Members

- Zoë Ravel — Head of Product (zoe@meridian.example)
- Nadia Hassan — PM (nadia@meridian.example)

## Processes owned

- Employee onboarding (owner: Zoë Ravel)
