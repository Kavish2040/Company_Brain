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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 9a45e3f3cf9c8894ab7822654ec7481d
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [180, 252]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [22, 74]
        quote: Let's keep the comp discussion in this channel only.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [180, 252]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
---

**Sam Kaur** (14:32): Let's keep the comp discussion in this channel only.

**Priya Raman** (14:39): Let's keep the comp discussion in this channel only.

**Priya Raman** (14:46): Compensation bands for the Engineering ladder need revisiting before Q3.
