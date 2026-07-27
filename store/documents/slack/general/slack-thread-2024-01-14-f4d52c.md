---
id: documents/slack/general/slack-thread-2024-01-14-f4d52c
type: Document
title: Slack thread — 2024-01-14
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-14.json
  external_id: slack/general/2024-01-14.json
  external_version: b689bdc27c17e7da
  content_sha256: b689bdc27c17e7da1eeef69280174f248dc6fe11b4743c406f7f40b1cbe6ffeb
timestamps:
  created: '2024-01-14T13:39:00Z'
  modified: '2024-01-14T13:53:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 4301f2e5b5604637f270614ff9786553
  status: accepted
relations:
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [47, 76]
        quote: Onboarding docs are in Drive.
---

**Nadia Hassan** (13:39): Welcome to the team! Onboarding docs are in Drive.

**Owen Fitzgerald** (13:46): Welcome to the team! Onboarding docs are in Drive.

**Sam Kelly** (13:53): Welcome to the team! Onboarding docs are in Drive.
