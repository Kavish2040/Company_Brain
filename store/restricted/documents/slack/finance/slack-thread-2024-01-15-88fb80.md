---
id: documents/slack/finance/slack-thread-2024-01-15-88fb80
type: Document
title: Slack thread — 2024-01-15
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/finance/2024-01-15.json
  external_id: slack/finance/2024-01-15.json
  external_version: 3088cd1066c3d2cd
  content_sha256: 3088cd1066c3d2cd380595203036319b71a8c2dd1855fc7298a88845becfd324
timestamps:
  created: '2024-01-15T09:07:00Z'
  modified: '2024-01-15T09:28:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 71b8c9a83d901b76f93f8f941e15f85e
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [189, 198]
        quote: Ana Brito
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 10]
        quote: Sam Kaur
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [292, 309]
        quote: Capacity planning
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [106, 122]
        quote: Release sign-off
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [169, 184]
        quote: security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [140, 151]
        quote: Engineering
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [214, 221]
        quote: Datadog
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [26, 35]
        quote: PagerDuty
---

**Sam Kaur** (09:07): The PagerDuty renewal lands in April. I own that end to end.

**Sam Kaur** (09:14): Release sign-off is blocked until Engineering signs off on the security review.

**Ana Brito** (09:21): The Datadog renewal lands in April. I own that end to end.

**Sam Kaur** (09:28): Capacity planning is blocked until Engineering signs off on the security review.
