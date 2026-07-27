---
id: documents/slack/support/slack-thread-2024-01-10-3ad37e
type: Document
title: Slack thread — 2024-01-10
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-10.json
  external_id: slack/support/2024-01-10.json
  external_version: 63197ac9496db246
  content_sha256: 63197ac9496db24653a21497b95000f3cb9da8c05f59a49e3498e87a07c19d5b
timestamps:
  created: '2024-01-10T11:43:00Z'
  modified: '2024-01-10T12:04:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 3fa876ec02799a0d8bb24e74698b603b
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [106, 117]
        quote: Priya Raman
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [294, 303]
        quote: Sam Kelly
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [82, 101]
        quote: Employee onboarding
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [171, 186]
        quote: Refund approval
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [357, 371]
        quote: Vendor renewal
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [67, 78]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [140, 147]
        quote: Finance
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [252, 261]
        quote: Snowflake
---

**Zoë Ravel** (11:43): This is the fourth ticket bounced back from Engineering on Employee onboarding.

**Priya Raman** (11:50): Looping in Finance for the refund side of Refund approval.

**Zoë Ravel** (11:57): Escalating this to Engineering — it's a Snowflake integration bug, not config.

**Sam Kelly** (12:04): Looping in Finance for the refund side of Vendor renewal.
