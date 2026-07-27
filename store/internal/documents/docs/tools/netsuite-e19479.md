---
id: documents/docs/tools/netsuite-e19479
type: Document
title: NetSuite
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/tools/netsuite.md
  external_id: docs/tools/netsuite.md
  external_version: 8664860c202add32
  content_sha256: 8664860c202add32fc9a4e0354c08f5ea6cc3dfa31af98fee196e89f033f49fd
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: ab8f1b8917a43f7d76cb5dc8837fe439
  status: accepted
relations:
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [12, 19]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [79, 86]
        quote: Product
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 10]
        quote: NetSuite
---

# NetSuite

Finance system of record; annual renewal each April.

Owned by the Product team.
