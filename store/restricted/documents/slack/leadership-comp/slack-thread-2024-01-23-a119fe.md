---
id: documents/slack/leadership-comp/slack-thread-2024-01-23-a119fe
type: Document
title: Slack thread — 2024-01-23
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-23.json
  external_id: slack/leadership-comp/2024-01-23.json
  external_version: b6dc8d1440725d2e
  content_sha256: b6dc8d1440725d2e00887c6a8f7d4f7f62c8eb76efbb9e8354d446f567c59464
timestamps:
  created: '2024-01-23T12:48:00Z'
  modified: '2024-01-23T12:55:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 68f87ed3f7656013928f3d85d4577459
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 13]
        quote: Priya Raman
---

**Priya Raman** (12:48): Let's keep the comp discussion in this channel only.

**Priya Raman** (12:55): Let's keep the comp discussion in this channel only.
