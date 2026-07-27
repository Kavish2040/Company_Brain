---
id: documents/slack/general/slack-thread-2024-01-13-85facb
type: Document
title: Slack thread — 2024-01-13
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-13.json
  external_id: slack/general/2024-01-13.json
  external_version: 1c8eca18e1501f56
  content_sha256: 1c8eca18e1501f562fdef38874e2927cf5d793c67c616c1282412864602ef517
timestamps:
  created: '2024-01-13T13:03:00Z'
  modified: '2024-01-13T13:24:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 23ea406c19c2ed676ccb392dc6f1f222
  status: accepted
relations:
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [45, 74]
        quote: Onboarding docs are in Drive.
---

**Tom Whelan** (13:03): Welcome to the team! Onboarding docs are in Drive.

**Ana Brito** (13:10): Welcome to the team! Onboarding docs are in Drive.

**Nadia Hassan** (13:17): All-hands moved to Thursday.

**Nadia Hassan** (13:24): All-hands moved to Thursday.
