---
id: documents/slack/general/slack-thread-2024-01-12-6735ce
type: Document
title: Slack thread — 2024-01-12
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-12.json
  external_id: slack/general/2024-01-12.json
  external_version: f24bb03f89203574
  content_sha256: f24bb03f892035742ab5e557d871d79222dd7873ceb56cefbccd837b9ca036cc
timestamps:
  created: '2024-01-12T11:28:00Z'
  modified: '2024-01-12T11:35:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 9c65e9da2fe30f2ee2a9f3ce6ca82a60
  status: accepted
relations:
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [43, 72]
        quote: Onboarding docs are in Drive.
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [100, 149]
        quote: Reminder that Vendor renewal kicks off next week.
---

**Sam Kaur** (11:28): Welcome to the team! Onboarding docs are in Drive.

**Nadia Hassan** (11:35): Reminder that Vendor renewal kicks off next week.
