---
id: documents/slack/leadership-comp/slack-thread-2024-01-09-25bcdf
type: Document
title: Slack thread — 2024-01-09
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-09.json
  external_id: slack/leadership-comp/2024-01-09.json
  external_version: b0280d2d6e176572
  content_sha256: b0280d2d6e17657218e164bf461f51b5056367041bf802d7907c263ac010bb34
timestamps:
  created: '2024-01-09T13:39:00Z'
  modified: '2024-01-09T13:46:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 98a02a52ef2f46c77b961783a6e4ae2c
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
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [81, 89]
        quote: Sam Kaur
---

**Priya Raman** (13:39): Let's keep the comp discussion in this channel only.

**Sam Kaur** (13:46): Let's keep the comp discussion in this channel only.
