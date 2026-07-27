---
id: documents/slack/leadership-comp/slack-thread-2024-01-13-d9f411
type: Document
title: Slack thread — 2024-01-13
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-13.json
  external_id: slack/leadership-comp/2024-01-13.json
  external_version: a8ed72ba47688b85
  content_sha256: a8ed72ba47688b854994b60c95e96e56d469323a18f7eb629496374b394db45f
timestamps:
  created: '2024-01-13T14:32:00Z'
  modified: '2024-01-13T14:46:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 7526c1b7b1ceb1c4ac348a35e387b914
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
        span: [207, 218]
        quote: Engineering
---

**Sam Kaur** (14:32): Let's keep the comp discussion in this channel only.

**Priya Raman** (14:39): Let's keep the comp discussion in this channel only.

**Priya Raman** (14:46): Compensation bands for the Engineering ladder need revisiting before Q3.
