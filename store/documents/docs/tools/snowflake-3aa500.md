---
id: documents/docs/tools/snowflake-3aa500
type: Document
title: Snowflake
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/tools/snowflake.md
  external_id: docs/tools/snowflake.md
  external_version: bcc332b7d837c3a7
  content_sha256: bcc332b7d837c3a74297dacdf374f53cc1103b9349635b82fb7768e34d705653
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: ab4d799e9ff3fc721e8879b81d56050f
  status: accepted
relations:
  - predicate: owns
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [80, 110]
        quote: Owned by the Engineering team.
---

# Snowflake

Data warehouse vendor. NOT the internal project of the same name.

Owned by the Engineering team.
