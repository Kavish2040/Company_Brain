---
id: documents/docs/tools/linear-b3cfb9
type: Document
title: Linear
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/tools/linear.md
  external_id: docs/tools/linear.md
  external_version: ebe6f43b94e90a8c
  content_sha256: ebe6f43b94e90a8c8e4f5846319d28892e086495e5734800786bf2a09970125a
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: b01a9405f76424bde0fd68acbaa87935
  status: accepted
relations:
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [10, 21]
        quote: Engineering
  - predicate: mentions
    object: tools/linear
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 8]
        quote: Linear
---

# Linear

Engineering issue tracking.

Owned by the Engineering team.
