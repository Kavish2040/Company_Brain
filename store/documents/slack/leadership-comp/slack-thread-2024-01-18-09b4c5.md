---
id: documents/slack/leadership-comp/slack-thread-2024-01-18-09b4c5
type: Document
title: Slack thread — 2024-01-18
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-18.json
  external_id: slack/leadership-comp/2024-01-18.json
  external_version: d3367f4378153adc
  content_sha256: d3367f4378153adc6eade1a7ff746b0b73c159876437e716fd594fa65d713a7f
timestamps:
  created: '2024-01-18T12:18:00Z'
  modified: '2024-01-18T12:25:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 7857504efb2f2eba6cb752fad53a9238
  status: accepted
relations:
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 10]
        quote: Sam Kaur
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [49, 60]
        quote: Engineering
---

**Sam Kaur** (12:18): Compensation bands for the Engineering ladder need revisiting before Q3.

**Sam Kaur** (12:25): Compensation bands for the Engineering ladder need revisiting before Q3.
