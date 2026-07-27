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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 8ebca52ee948841fe5733b7cc06ee708
  status: accepted
relations:
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [47, 76]
        quote: Onboarding docs are in Drive.
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [107, 157]
        quote: Reminder that Quarterly close kicks off next week.
---

**Nadia Hassan** (14:20): Welcome to the team! Onboarding docs are in Drive.

**Owen Fitzgerald** (14:27): Reminder that Quarterly close kicks off next week.
