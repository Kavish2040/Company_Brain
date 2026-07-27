---
id: documents/slack/general/slack-thread-2024-01-11-682e3c
type: Document
title: Slack thread — 2024-01-11
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: slack
  uri: file://corpus/slack/general/2024-01-11.json
  external_id: general/2024-01-11
  external_version: rev-0
  content_sha256: 7b5176177e5cfd5c05f75984000f66dd30e787c2e0530aa33b3315944c7b3a5f
timestamps:
  created: '2024-01-11T10:37:00Z'
  modified: '2024-01-11T10:44:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: b3f12201f134b5fd63193b7bc6cd7bb4
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [77, 88]
        quote: Priya Raman
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: Sam Kelly
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [37, 52]
        quote: Quarterly close
---

**Sam Kelly** (10:37): Reminder that Quarterly close kicks off next week.

**Priya Raman** (10:44): All-hands moved to Thursday.
