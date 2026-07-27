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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 25296379e33c3534170b68b182c63038
  status: accepted
relations:
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.55
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [38, 64]
        quote: annual renewal each April.
  - predicate: mentions
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [12, 64]
        quote: Finance system of record; annual renewal each April.
  - predicate: owns
    subject: teams/product
    object: tools/netsuite
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [66, 92]
        quote: Owned by the Product team.
---

# NetSuite

Finance system of record; annual renewal each April.

Owned by the Product team.
