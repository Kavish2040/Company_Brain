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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: cb8785348e566c2b864bc9ea498ebed2
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/quarterly-close
    object: processes/release-signoff
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [133, 209]
        quote: Deploy for the Quarterly close change is queued behind the release sign-off.
  - predicate: handoff_to
    subject: processes/release-signoff
    object: teams/support
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [25, 106]
        quote: Handing the Release sign-off ticket over to Support, they own the customer comms.
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [234, 298]
        quote: The NetSuite alert fired again overnight — third time this week.
---

**Priya Raman** (12:58): Handing the Release sign-off ticket over to Support, they own the customer comms.

**Priya Raman** (13:05): Deploy for the Quarterly close change is queued behind the release sign-off.

**Sam Kelly** (13:12): The NetSuite alert fired again overnight — third time this week.
