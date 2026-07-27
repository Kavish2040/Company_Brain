---
id: documents/slack/leadership-comp/slack-thread-2024-01-14-931c9a
type: Document
title: Slack thread — 2024-01-14
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-14.json
  external_id: slack/leadership-comp/2024-01-14.json
  external_version: 7824291ec38f2d28
  content_sha256: 7824291ec38f2d284bd18a00be411aab9b0ec59c3bb639e890b044440340e8ee
timestamps:
  created: '2024-01-14T12:44:00Z'
  modified: '2024-01-14T12:58:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 84f6e5121b1773fd0262948eaa47597b
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

**Sam Kaur** (12:44): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (12:51): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (12:58): Let's keep the comp discussion in this channel only.
