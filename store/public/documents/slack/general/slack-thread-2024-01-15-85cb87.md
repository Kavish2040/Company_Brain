---
id: documents/slack/general/slack-thread-2024-01-15-85cb87
type: Document
title: Slack thread — 2024-01-15
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-15.json
  external_id: slack/general/2024-01-15.json
  external_version: 15cd72ed3974ecfc
  content_sha256: 15cd72ed3974ecfc184955a9ac2ac2ddee63ae546e48598e16a91c502dccd29c
timestamps:
  created: '2024-01-15T10:16:00Z'
  modified: '2024-01-15T10:30:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 083809a00b7995a3e1c2f09ad5df4bfb
  status: accepted
relations:
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [22, 76]
        quote: Reminder that Customer escalation kicks off next week.
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [123, 152]
        quote: Onboarding docs are in Drive.
---

**Sam Kaur** (10:16): Reminder that Customer escalation kicks off next week.

**Tom Whelan** (10:23): Welcome to the team! Onboarding docs are in Drive.

**Priya Raman** (10:30): Welcome to the team! Onboarding docs are in Drive.
