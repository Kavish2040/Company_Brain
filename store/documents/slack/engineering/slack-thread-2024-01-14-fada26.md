---
id: documents/slack/engineering/slack-thread-2024-01-14-fada26
type: Document
title: Slack thread — 2024-01-14
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-14.json
  external_id: slack/engineering/2024-01-14.json
  external_version: 336147d8ebcbda65
  content_sha256: 336147d8ebcbda6574135429c4c33a92dd5746ad0670dece0fbb740a7ab5baa2
timestamps:
  created: '2024-01-14T11:03:00Z'
  modified: '2024-01-14T11:10:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: acc96bd1d70fcad48c14a220daffd7d8
  status: accepted
relations:
  - predicate: depends_on
    object: processes/release-signoff
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [25, 101]
        quote: Deploy for the Security review change is queued behind the release sign-off.
  - predicate: handoff_to
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [127, 213]
        quote: Handing the Customer data request ticket over to Support, they own the customer comms.
---

**Priya Raman** (11:03): Deploy for the Security review change is queued behind the release sign-off.

**Tom Whelan** (11:10): Handing the Customer data request ticket over to Support, they own the customer comms.
