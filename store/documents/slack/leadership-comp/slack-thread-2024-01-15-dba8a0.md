---
id: documents/slack/leadership-comp/slack-thread-2024-01-15-dba8a0
type: Document
title: Slack thread — 2024-01-15
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-15.json
  external_id: slack/leadership-comp/2024-01-15.json
  external_version: 6de55731261dccea
  content_sha256: 6de55731261dccea4de118b0eff59583b666117331b8e8157732ac923f9146ec
timestamps:
  created: '2024-01-15T11:14:00Z'
  modified: '2024-01-15T11:35:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: eeef9349a47ab9ef1ac340a32072a61e
  status: accepted
relations:
  - predicate: mentions
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [256, 328]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
---

**Sam Kaur** (11:14): Let's keep the comp discussion in this channel only.

**Priya Raman** (11:21): Let's keep the comp discussion in this channel only.

**Priya Raman** (11:28): Let's keep the comp discussion in this channel only.

**Sam Kaur** (11:35): Compensation bands for the Engineering ladder need revisiting before Q3.
