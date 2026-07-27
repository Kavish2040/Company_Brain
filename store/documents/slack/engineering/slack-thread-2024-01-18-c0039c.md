---
id: documents/slack/engineering/slack-thread-2024-01-18-c0039c
type: Document
title: Slack thread — 2024-01-18
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-18.json
  external_id: slack/engineering/2024-01-18.json
  external_version: a565db525bfd86c7
  content_sha256: a565db525bfd86c751a77d9aaa4916afada26660dd75c27719689fcb00b4f7a0
timestamps:
  created: '2024-01-18T13:17:00Z'
  modified: '2024-01-18T13:24:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 8eed4c35f9331b872f1290452a821364
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 14]
        quote: Dev Oyelaran
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [38, 59]
        quote: Customer data request
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [157, 164]
        quote: Finance
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [75, 82]
        quote: Support
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [177, 186]
        quote: Snowflake
---

**Dev Oyelaran** (13:17): Handing the Customer data request ticket over to Support, they own the customer comms.

**Dev Oyelaran** (13:24): Can someone from Finance confirm the Snowflake renewal date?
