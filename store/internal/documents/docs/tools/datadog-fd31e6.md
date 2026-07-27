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
  prompt_version: claude-roster-v2
  cache_key: 736aeff32eb0bf2cc24998fd0923d158
  status: accepted
relations:
  - predicate: owns
    subject: teams/support
    object: tools/datadog
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
