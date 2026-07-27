---
id: documents/slack/leadership-comp/slack-thread-2024-01-22-1ee959
type: Document
title: Slack thread — 2024-01-22
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-22.json
  external_id: slack/leadership-comp/2024-01-22.json
  external_version: a20dcf5e749d4e7c
  content_sha256: a20dcf5e749d4e7cb033b3257c5a62c84b47864e408241c7732fbdc35dff4e9a
timestamps:
  created: '2024-01-22T12:14:00Z'
  modified: '2024-01-22T12:35:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: ff574e19a9a73de6195c0acf3328dc84
  status: accepted
relations:
  - predicate: mentions
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [22, 94]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
---

**Sam Kaur** (12:14): Compensation bands for the Engineering ladder need revisiting before Q3.

**Sam Kaur** (12:21): Compensation bands for the Engineering ladder need revisiting before Q3.

**Sam Kaur** (12:28): Compensation bands for the Engineering ladder need revisiting before Q3.

**Sam Kaur** (12:35): Let's keep the comp discussion in this channel only.
