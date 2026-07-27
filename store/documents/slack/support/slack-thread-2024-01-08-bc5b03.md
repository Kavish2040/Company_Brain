---
id: documents/slack/support/slack-thread-2024-01-08-bc5b03
type: Document
title: Slack thread — 2024-01-08
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-08.json
  external_id: slack/support/2024-01-08.json
  external_version: 6ef0720b1b4ab6e8
  content_sha256: 6ef0720b1b4ab6e83adc2643d16bfd5f7f14b01ec575c8a1014655e26dd4f960
timestamps:
  created: '2024-01-08T14:12:00Z'
  modified: '2024-01-08T14:26:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: b32fb7b7d954ca70075a30abeaa7114e
  status: accepted
relations:
  - predicate: handoff_to
    object: teams/engineering
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [132, 210]
        quote: Escalating this to Engineering — it's a Snowflake integration bug, not config.
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [26, 105]
        quote: This is the fourth ticket bounced back from Engineering on Customer escalation.
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [235, 310]
        quote: This is the fourth ticket bounced back from Engineering on Security review.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [26, 105]
        quote: This is the fourth ticket bounced back from Engineering on Customer escalation.
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [132, 210]
        quote: Escalating this to Engineering — it's a Snowflake integration bug, not config.
---

**Dev Oyelaran** (14:12): This is the fourth ticket bounced back from Engineering on Customer escalation.

**Priya Raman** (14:19): Escalating this to Engineering — it's a Snowflake integration bug, not config.

**Zoë Ravel** (14:26): This is the fourth ticket bounced back from Engineering on Security review.
