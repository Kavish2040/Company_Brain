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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: b493a2e772c10c7b4eccdd5db80ea3dc
  status: accepted
relations:
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [53, 60]
        quote: Support
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 9]
        quote: Datadog
---

# Datadog

Observability and alerting.

Owned by the Support team.
