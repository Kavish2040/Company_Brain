---
id: documents/slack/leadership-comp/slack-thread-2024-01-19-c99a8d
type: Document
title: Slack thread — 2024-01-19
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/leadership-comp/2024-01-19.json
  external_id: leadership-comp/2024-01-19
  external_version: rev-0
  content_sha256: 10c15da634ea0f8ad525af62f8df3743f5784d5b519037d4b337a44af2b1f3f6
timestamps:
  created: '2024-01-19T09:47:00Z'
  modified: '2024-01-19T10:08:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 938bf8a2db0c66b0206c3802d6d1d5c1
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 13]
        quote: Priya Raman
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [52, 63]
        quote: Engineering
---

**Priya Raman** (09:47): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (09:54): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (10:01): Let's keep the comp discussion in this channel only.

**Priya Raman** (10:08): Compensation bands for the Engineering ladder need revisiting before Q3.
