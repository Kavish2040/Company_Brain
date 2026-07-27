---
id: documents/slack/support/slack-thread-2024-01-14-af5f62
type: Document
title: Slack thread — 2024-01-14
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-14.json
  external_id: slack/support/2024-01-14.json
  external_version: 9043fa4818d3beab
  content_sha256: 9043fa4818d3beab343642d2f57600cee067dd933a028136261e910e8ba88f13
timestamps:
  created: '2024-01-14T09:28:00Z'
  modified: '2024-01-14T09:42:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 3515650d20bb1728c66f77f61d57b21f
  status: accepted
relations:
  - predicate: handoff_to
    subject: processes/release-signoff
    object: teams/finance
    confidence: 0.65
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [25, 84]
        quote: Looping in Finance for the refund side of Release sign-off.
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [112, 174]
        quote: Customer is asking about the Capacity planning timeline again.
---

**Priya Raman** (09:28): Looping in Finance for the refund side of Release sign-off.

**Nadia Hassan** (09:35): Customer is asking about the Capacity planning timeline again.

**Zoë Ravel** (09:42): Looping in Finance for the refund side of Quarterly close.
