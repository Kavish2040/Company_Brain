---
id: documents/slack/engineering/slack-thread-2024-01-16-f8f188
type: Document
title: Slack thread — 2024-01-16
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-16.json
  external_id: slack/engineering/2024-01-16.json
  external_version: 683e04b0a894b41d
  content_sha256: 683e04b0a894b41d6373e9b1a4b9a9514e10f0a13265c39194542be126158094
timestamps:
  created: '2024-01-16T14:44:00Z'
  modified: '2024-01-16T14:58:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 31041a5e189ff37badcb7aba6d383ad6
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: Ana Brito
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [192, 203]
        quote: Priya Raman
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [227, 246]
        quote: Customer escalation
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [38, 53]
        quote: Quarterly close
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [82, 98]
        quote: release sign-off
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [262, 269]
        quote: Support
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [128, 136]
        quote: NetSuite
---

**Ana Brito** (14:44): Deploy for the Quarterly close change is queued behind the release sign-off.

**Ana Brito** (14:51): The NetSuite alert fired again overnight — third time this week.

**Priya Raman** (14:58): Handing the Customer escalation ticket over to Support, they own the customer comms.
