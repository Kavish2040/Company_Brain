---
id: documents/slack/leadership-comp/slack-thread-2024-01-10-05cdd2
type: Document
title: Slack thread — 2024-01-10
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-10.json
  external_id: slack/leadership-comp/2024-01-10.json
  external_version: b37b5d22c6a99b88
  content_sha256: b37b5d22c6a99b88265e116c2b319d8674a0b51d1c23fe25ec9415a748b5098e
timestamps:
  created: '2024-01-10T14:27:00Z'
  modified: '2024-01-10T14:41:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: e5832cbce511491a32771f0b92a09473
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

**Sam Kaur** (14:27): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (14:34): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (14:41): Compensation bands for the Engineering ladder need revisiting before Q3.
