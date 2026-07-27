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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 947c75a8e5fc7c2ae63da1a9694918bc
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [156, 167]
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
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [80, 90]
        quote: Tom Whelan
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [36, 55]
        quote: Customer escalation
---

**Sam Kaur** (10:16): Reminder that Customer escalation kicks off next week.

**Tom Whelan** (10:23): Welcome to the team! Onboarding docs are in Drive.

**Priya Raman** (10:30): Welcome to the team! Onboarding docs are in Drive.
