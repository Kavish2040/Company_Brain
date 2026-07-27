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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 603f9d9756501c96c519beb60cd9186e
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [96, 193]
        quote: '**Priya Raman** (14:34): Compensation bands for the Engineering ladder need revisiting before Q3.'
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [0, 94]
        quote: '**Sam Kaur** (14:27): Compensation bands for the Engineering ladder need revisiting before Q3.'
  - predicate: mentions
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [22, 94]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
---

**Sam Kaur** (14:27): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (14:34): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (14:41): Compensation bands for the Engineering ladder need revisiting before Q3.
