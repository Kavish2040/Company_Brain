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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 2a4ddab70e3ae9294e1a9bc4d2aa2130
  status: accepted
relations:
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [71, 163]
        quote: 'Not to be confused with Snowflake the vendor, which is the target

          platform for this project.'
---

# Project Snowflake

Internal codename for the Q2 warehouse migration.
Not to be confused with Snowflake the vendor, which is the target
platform for this project. Led by Tom Whelan.
