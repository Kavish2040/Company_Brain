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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 857d7c806a3e64cb6eae46930e9bc678
  status: accepted
relations:
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [93, 104]
        quote: Engineering
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: Snowflake
---

# Snowflake

Data warehouse vendor. NOT the internal project of the same name.

Owned by the Engineering team.
