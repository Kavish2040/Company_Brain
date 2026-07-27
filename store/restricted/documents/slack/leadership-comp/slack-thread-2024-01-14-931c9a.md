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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 149705c4db84e4dc42c4ce32de7c78d8
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [98, 109]
        quote: Priya Raman
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

**Sam Kaur** (12:44): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (12:51): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (12:58): Let's keep the comp discussion in this channel only.
