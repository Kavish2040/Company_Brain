---
id: documents/slack/general/slack-thread-2024-01-09-bd6c7a
type: Document
title: Slack thread — 2024-01-09
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-09.json
  external_id: slack/general/2024-01-09.json
  external_version: e9c349bee8b88b99
  content_sha256: e9c349bee8b88b99a742005443e76dd317f6037a0127fd7fa06052c597328e20
timestamps:
  created: '2024-01-09T09:20:00Z'
  modified: '2024-01-09T09:41:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: b671b5c5e3f84bb590d0499420655054
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [138, 148]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [83, 94]
        quote: Priya Raman
---

**Owen Fitzgerald** (09:20): Welcome to the team! Onboarding docs are in Drive.

**Priya Raman** (09:27): All-hands moved to Thursday.

**Mei Tanaka** (09:34): Welcome to the team! Onboarding docs are in Drive.

**Mei Tanaka** (09:41): Welcome to the team! Onboarding docs are in Drive.
