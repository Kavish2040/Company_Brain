---
id: documents/slack/general/slack-thread-2024-01-08-16cb6b
type: Document
title: Slack thread — 2024-01-08
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-08.json
  external_id: slack/general/2024-01-08.json
  external_version: 6cc13dfe41b68b0d
  content_sha256: 6cc13dfe41b68b0d0e0e00dbf46c7c25f05251fda9d283d522a8cd4db04a98e9
timestamps:
  created: '2024-01-08T13:56:00Z'
  modified: '2024-01-08T14:03:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 051a08a179bea679383064b4259c830e
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [81, 155]
        quote: 'Nadia Hassan** (14:03): Reminder that Quarterly close kicks off next week.'
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [2, 77]
        quote: 'Sam Kelly** (13:56): Reminder that Employee onboarding kicks off next week.'
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [23, 77]
        quote: Reminder that Employee onboarding kicks off next week.
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [105, 155]
        quote: Reminder that Quarterly close kicks off next week.
---

**Sam Kelly** (13:56): Reminder that Employee onboarding kicks off next week.

**Nadia Hassan** (14:03): Reminder that Quarterly close kicks off next week.
