---
id: documents/slack/leadership-comp/slack-thread-2024-01-17-1fcf57
type: Document
title: Slack thread — 2024-01-17
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/leadership-comp/2024-01-17.json
  external_id: leadership-comp/2024-01-17
  external_version: rev-0
  content_sha256: c48c55bd8b69a6578679bfab0bd71b8cdf446b8b542cb34682803238554407b2
timestamps:
  created: '2024-01-17T09:11:00Z'
  modified: '2024-01-17T09:32:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 0ea278e7d95c83c4b367de5dff556584
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

**Sam Kaur** (09:11): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (09:18): Let's keep the comp discussion in this channel only.

**Sam Kaur** (09:25): Compensation bands for the Engineering ladder need revisiting before Q3.

**Sam Kaur** (09:32): Compensation bands for the Engineering ladder need revisiting before Q3.
