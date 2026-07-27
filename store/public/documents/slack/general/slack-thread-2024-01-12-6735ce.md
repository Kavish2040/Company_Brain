---
id: documents/slack/general/slack-thread-2024-01-12-6735ce
type: Document
title: Slack thread — 2024-01-12
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: slack
  uri: file://corpus/slack/general/2024-01-12.json
  external_id: general/2024-01-12
  external_version: rev-0
  content_sha256: f24bb03f892035742ab5e557d871d79222dd7873ceb56cefbccd837b9ca036cc
timestamps:
  created: '2024-01-12T11:28:00Z'
  modified: '2024-01-12T11:35:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 47f94409607086ef1c3f22c29f112653
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [76, 88]
        quote: Nadia Hassan
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
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [114, 128]
        quote: Vendor renewal
---

**Sam Kaur** (11:28): Welcome to the team! Onboarding docs are in Drive.

**Nadia Hassan** (11:35): Reminder that Vendor renewal kicks off next week.
