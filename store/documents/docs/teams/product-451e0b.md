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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 9c78913e5547b05ae3f8bd899e5373b1
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [78, 120]
        quote: Nadia Hassan — PM (nadia@meridian.example)
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [25, 75]
        quote: Zoë Ravel — Head of Product (zoe@meridian.example)
  - predicate: mentions
    object: teams/product
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [0, 9]
        quote: '# Product'
  - predicate: owns
    object: processes/onboarding
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [144, 182]
        quote: 'Employee onboarding (owner: Zoë Ravel)'
---

# Product

## Members

- Zoë Ravel — Head of Product (zoe@meridian.example)
- Nadia Hassan — PM (nadia@meridian.example)

## Processes owned

- Employee onboarding (owner: Zoë Ravel)
