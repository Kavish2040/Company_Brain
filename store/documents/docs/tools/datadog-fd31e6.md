---
id: documents/docs/tools/datadog-fd31e6
type: Document
title: Datadog
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/tools/datadog.md
  external_id: docs/tools/datadog.md
  external_version: 21bcbab38c2d745c
  content_sha256: 21bcbab38c2d745c7f438ac0ddec705e72c83462bd8de1a16e5d279585860b5f
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 04b8af78cc1647ccdc87106cadd986c1
  status: accepted
relations:
  - predicate: owns
    object: teams/support
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [40, 66]
        quote: Owned by the Support team.
---

# Datadog

Observability and alerting.

Owned by the Support team.
