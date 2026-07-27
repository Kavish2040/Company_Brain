---
id: documents/slack/leadership-comp/slack-thread-2024-01-15-dba8a0
type: Document
title: Slack thread — 2024-01-15
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/leadership-comp/2024-01-15.json
  external_id: leadership-comp/2024-01-15
  external_version: rev-0
  content_sha256: 6de55731261dccea4de118b0eff59583b666117331b8e8157732ac923f9146ec
timestamps:
  created: '2024-01-15T11:14:00Z'
  modified: '2024-01-15T11:35:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: f9cddd9bea6267155a6837e1aaeacf06
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [78, 89]
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
        span: [283, 294]
        quote: Engineering
---

**Sam Kaur** (11:14): Let's keep the comp discussion in this channel only.

**Priya Raman** (11:21): Let's keep the comp discussion in this channel only.

**Priya Raman** (11:28): Let's keep the comp discussion in this channel only.

**Sam Kaur** (11:35): Compensation bands for the Engineering ladder need revisiting before Q3.
