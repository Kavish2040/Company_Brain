---
id: documents/slack/leadership-comp/slack-thread-2024-01-19-c99a8d
type: Document
title: Slack thread — 2024-01-19
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-19.json
  external_id: slack/leadership-comp/2024-01-19.json
  external_version: 10c15da634ea0f8a
  content_sha256: 10c15da634ea0f8ad525af62f8df3743f5784d5b519037d4b337a44af2b1f3f6
timestamps:
  created: '2024-01-19T09:47:00Z'
  modified: '2024-01-19T10:08:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 45835e292a4a8cf0a6e4413b31c19ff3
  status: accepted
relations:
  - predicate: mentions
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [25, 97]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
---

**Priya Raman** (09:47): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (09:54): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (10:01): Let's keep the comp discussion in this channel only.

**Priya Raman** (10:08): Compensation bands for the Engineering ladder need revisiting before Q3.
