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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: fb53cabf7f747183014115d346179963
  status: accepted
relations:
  - predicate: handoff_to
    subject: processes/onboarding
    object: teams/engineering
    confidence: 0.45
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [212, 290]
        quote: Escalating this to Engineering — it's a Snowflake integration bug, not config.
  - predicate: handoff_to
    subject: processes/vendor-renewal
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [315, 372]
        quote: Looping in Finance for the refund side of Vendor renewal.
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 102]
        quote: This is the fourth ticket bounced back from Engineering on Employee onboarding.
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [129, 187]
        quote: Looping in Finance for the refund side of Refund approval.
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [315, 372]
        quote: Looping in Finance for the refund side of Vendor renewal.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 102]
        quote: This is the fourth ticket bounced back from Engineering on Employee onboarding.
  - predicate: mentions
    object: teams/finance
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [129, 187]
        quote: Looping in Finance for the refund side of Refund approval.
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [212, 290]
        quote: Escalating this to Engineering — it's a Snowflake integration bug, not config.
---

**Zoë Ravel** (11:43): This is the fourth ticket bounced back from Engineering on Employee onboarding.

**Priya Raman** (11:50): Looping in Finance for the refund side of Refund approval.

**Zoë Ravel** (11:57): Escalating this to Engineering — it's a Snowflake integration bug, not config.

**Sam Kelly** (12:04): Looping in Finance for the refund side of Vendor renewal.
