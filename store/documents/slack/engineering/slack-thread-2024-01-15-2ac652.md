---
id: documents/slack/engineering/slack-thread-2024-01-15-2ac652
type: Document
title: Slack thread — 2024-01-15
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-15.json
  external_id: slack/engineering/2024-01-15.json
  external_version: 1a9891ff944fb8ac
  content_sha256: 1a9891ff944fb8ac4d83b3ff8f823bfff0d2fc82bb1644040c4c840ccfbc64dc
timestamps:
  created: '2024-01-15T12:58:00Z'
  modified: '2024-01-15T13:12:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: fb2605f346d39f007fcdc08ea01aced8
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 13]
        quote: Priya Raman
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [213, 222]
        quote: Sam Kelly
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [148, 163]
        quote: Quarterly close
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [37, 53]
        quote: Release sign-off
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [69, 76]
        quote: Support
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [238, 246]
        quote: NetSuite
---

**Priya Raman** (12:58): Handing the Release sign-off ticket over to Support, they own the customer comms.

**Priya Raman** (13:05): Deploy for the Quarterly close change is queued behind the release sign-off.

**Sam Kelly** (13:12): The NetSuite alert fired again overnight — third time this week.
