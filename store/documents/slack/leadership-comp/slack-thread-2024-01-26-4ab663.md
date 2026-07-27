---
id: documents/slack/leadership-comp/slack-thread-2024-01-26-4ab663
type: Document
title: Slack thread — 2024-01-26
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-26.json
  external_id: slack/leadership-comp/2024-01-26.json
  external_version: ab53e364a37440fc
  content_sha256: ab53e364a37440fce95963fc7ea5ecec05c30792a9eeb960272e9d073f35845a
timestamps:
  created: '2024-01-26T12:34:00Z'
  modified: '2024-01-26T12:55:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 4290f0303753333de942c0264cd58bc4
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [270, 281]
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

**Sam Kaur** (12:34): Compensation bands for the Engineering ladder need revisiting before Q3.

**Sam Kaur** (12:41): Compensation bands for the Engineering ladder need revisiting before Q3.

**Sam Kaur** (12:48): Let's keep the comp discussion in this channel only.

**Priya Raman** (12:55): Let's keep the comp discussion in this channel only.
