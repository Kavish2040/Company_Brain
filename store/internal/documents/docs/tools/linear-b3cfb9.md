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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 9836f67c9447cafabe7cf3131308d72f
  status: accepted
relations:
  - predicate: owns
    subject: teams/engineering
    object: tools/linear
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [39, 69]
        quote: Owned by the Engineering team.
---

# Linear

Engineering issue tracking.

Owned by the Engineering team.
