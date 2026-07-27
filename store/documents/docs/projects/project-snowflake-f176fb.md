---
id: documents/docs/projects/project-snowflake-f176fb
type: Document
title: Project Snowflake
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/projects/snowflake.md
  external_id: docs/projects/snowflake.md
  external_version: e37af53637e77147
  content_sha256: e37af53637e7714785c22b749967ca4798c5e2f3b9c6ae251ed620316f0eff42
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 1f6f44fd1f38c9e234cb7f36535d1cac
  status: accepted
relations:
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [171, 181]
        quote: Tom Whelan
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [10, 19]
        quote: Snowflake
---

# Project Snowflake

Internal codename for the Q2 warehouse migration.
Not to be confused with Snowflake the vendor, which is the target
platform for this project. Led by Tom Whelan.
