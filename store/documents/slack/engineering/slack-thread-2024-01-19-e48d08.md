---
id: documents/slack/engineering/slack-thread-2024-01-19-e48d08
type: Document
title: Slack thread — 2024-01-19
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-19.json
  external_id: slack/engineering/2024-01-19.json
  external_version: ce44975063bee487
  content_sha256: ce44975063bee487b2007221ed85a5c90442033ee747bfdf1fd09b84c0fe5e5e
timestamps:
  created: '2024-01-19T12:39:00Z'
  modified: '2024-01-19T12:46:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 65ec6ac9884bd4de7c3b0e38107a2b36
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [93, 105]
        quote: Dev Oyelaran
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
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [129, 148]
        quote: Customer escalation
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [164, 171]
        quote: Support
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [29, 37]
        quote: NetSuite
---

**Priya Raman** (12:39): The NetSuite alert fired again overnight — third time this week.

**Dev Oyelaran** (12:46): Handing the Customer escalation ticket over to Support, they own the customer comms.
