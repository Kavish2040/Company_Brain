---
id: documents/slack/leadership-comp/slack-thread-2024-01-16-d0a584
type: Document
title: Slack thread — 2024-01-16
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-16.json
  external_id: slack/leadership-comp/2024-01-16.json
  external_version: dd750ad49ac3ec67
  content_sha256: dd750ad49ac3ec67414ea785b6f195e809c6d7e59678fab5f0d100c426c39311
timestamps:
  created: '2024-01-16T11:10:00Z'
  modified: '2024-01-16T11:31:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: b9d0f3f8fa9f3dca0181f6f5bc6d721a
  status: accepted
relations:
  - predicate: mentions
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [253, 325]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
---

**Sam Kaur** (11:10): Let's keep the comp discussion in this channel only.

**Priya Raman** (11:17): Let's keep the comp discussion in this channel only.

**Sam Kaur** (11:24): Let's keep the comp discussion in this channel only.

**Sam Kaur** (11:31): Compensation bands for the Engineering ladder need revisiting before Q3.
