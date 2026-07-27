---
id: documents/slack/general/slack-thread-2024-01-19-2aee4f
type: Document
title: Slack thread — 2024-01-19
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-19.json
  external_id: slack/general/2024-01-19.json
  external_version: b570802415c8933b
  content_sha256: b570802415c8933bee2a8c578aceb3acb3f69112204bcba111c609b982d2289b
timestamps:
  created: '2024-01-19T14:20:00Z'
  modified: '2024-01-19T14:27:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 89d2a947405352aed0d433738702fc74
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 14]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [80, 95]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [121, 136]
        quote: Quarterly close
---

**Nadia Hassan** (14:20): Welcome to the team! Onboarding docs are in Drive.

**Owen Fitzgerald** (14:27): Reminder that Quarterly close kicks off next week.
