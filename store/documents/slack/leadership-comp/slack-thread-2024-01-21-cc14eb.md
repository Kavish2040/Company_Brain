---
id: documents/slack/leadership-comp/slack-thread-2024-01-21-cc14eb
type: Document
title: Slack thread — 2024-01-21
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-21.json
  external_id: slack/leadership-comp/2024-01-21.json
  external_version: c54d48ac72e47316
  content_sha256: c54d48ac72e4731691c4d335974da170c58209fbfaa5ceba0107cd149e8dff00
timestamps:
  created: '2024-01-21T14:22:00Z'
  modified: '2024-01-21T14:43:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: ecd8aa80b006c8e41a2c30c675a811d5
  status: accepted
relations:
  - predicate: mentions
    object: teams/engineering
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [177, 249]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
---

**Sam Kaur** (14:22): Let's keep the comp discussion in this channel only.

**Priya Raman** (14:29): Let's keep the comp discussion in this channel only.

**Sam Kaur** (14:36): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (14:43): Compensation bands for the Engineering ladder need revisiting before Q3.
