---
id: documents/slack/general/slack-thread-2024-01-08-16cb6b
type: Document
title: Slack thread — 2024-01-08
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: slack
  uri: file://corpus/slack/general/2024-01-08.json
  external_id: general/2024-01-08
  external_version: rev-0
  content_sha256: 6cc13dfe41b68b0d0e0e00dbf46c7c25f05251fda9d283d522a8cd4db04a98e9
timestamps:
  created: '2024-01-08T13:56:00Z'
  modified: '2024-01-08T14:03:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: aa0afb25ec8733c40698173880f8666c
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [81, 93]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: Sam Kelly
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [37, 56]
        quote: Employee onboarding
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [119, 134]
        quote: Quarterly close
---

**Sam Kelly** (13:56): Reminder that Employee onboarding kicks off next week.

**Nadia Hassan** (14:03): Reminder that Quarterly close kicks off next week.
