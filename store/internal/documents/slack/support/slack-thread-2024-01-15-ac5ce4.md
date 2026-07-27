---
id: documents/slack/support/slack-thread-2024-01-15-ac5ce4
type: Document
title: Slack thread — 2024-01-15
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: slack
  uri: file://corpus/slack/support/2024-01-15.json
  external_id: support/2024-01-15
  external_version: rev-0
  content_sha256: 1b951c1b0e4d86ba0342ba91aaef0ecbef01ccd53e2dbe3dd926575fcfab7300
timestamps:
  created: '2024-01-15T14:32:00Z'
  modified: '2024-01-15T14:53:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 307c6638433f68885afade747f1185a3
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [189, 201]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 12]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [292, 303]
        quote: Priya Raman
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [103, 111]
        quote: Sam Kaur
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [152, 169]
        quote: Incident response
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [83, 98]
        quote: Refund approval
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [357, 373]
        quote: Release sign-off
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [68, 79]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [326, 333]
        quote: Finance
---

**Mei Tanaka** (14:32): This is the fourth ticket bounced back from Engineering on Refund approval.

**Sam Kaur** (14:39): Customer is asking about the Incident response timeline again.

**Dev Oyelaran** (14:46): This is the fourth ticket bounced back from Engineering on Refund approval.

**Priya Raman** (14:53): Looping in Finance for the refund side of Release sign-off.
