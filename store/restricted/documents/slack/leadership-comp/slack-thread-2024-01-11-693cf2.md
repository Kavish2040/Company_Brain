---
id: documents/slack/leadership-comp/slack-thread-2024-01-11-693cf2
type: Document
title: Slack thread — 2024-01-11
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-11.json
  external_id: slack/leadership-comp/2024-01-11.json
  external_version: 333861b16ed0b76c
  content_sha256: 333861b16ed0b76c83a19355c2a36dbb917484edc8a4ecec5db38712574cf885
timestamps:
  created: '2024-01-11T10:03:00Z'
  modified: '2024-01-11T10:24:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 5004d51e488021f309fc7ef0785f592c
  status: accepted
relations:
  - predicate: mentions
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [25, 97]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
---

**Priya Raman** (10:03): Compensation bands for the Engineering ladder need revisiting before Q3.

**Sam Kaur** (10:10): Let's keep the comp discussion in this channel only.

**Priya Raman** (10:17): Let's keep the comp discussion in this channel only.

**Sam Kaur** (10:24): Compensation bands for the Engineering ladder need revisiting before Q3.
