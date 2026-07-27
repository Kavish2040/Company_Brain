---
id: documents/slack/general/slack-thread-2024-01-26-646ace
type: Document
title: Slack thread — 2024-01-26
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-26.json
  external_id: slack/general/2024-01-26.json
  external_version: 373de7373e6288f2
  content_sha256: 373de7373e6288f2c03735f0d8b18c6d292016f5fef64797c2518083c11d89d2
timestamps:
  created: '2024-01-26T11:47:00Z'
  modified: '2024-01-26T12:08:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 59e72711dfcb373f8bbbae0e1de96dd7
  status: accepted
relations:
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [268, 308]
        quote: Employee onboarding kicks off next week.
---

**Sam Kelly** (11:47): Welcome to the team! Onboarding docs are in Drive.

**Tom Whelan** (11:54): Welcome to the team! Onboarding docs are in Drive.

**Dev Oyelaran** (12:01): Welcome to the team! Onboarding docs are in Drive.

**Priya Raman** (12:08): Reminder that Employee onboarding kicks off next week.
