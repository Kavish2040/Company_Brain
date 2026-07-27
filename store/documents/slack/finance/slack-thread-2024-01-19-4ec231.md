---
id: documents/slack/finance/slack-thread-2024-01-19-4ec231
type: Document
title: Slack thread — 2024-01-19
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/finance/2024-01-19.json
  external_id: slack/finance/2024-01-19.json
  external_version: 8c76891ddcd217a9
  content_sha256: 8c76891ddcd217a9d8da635c43b2da24886c7342885f4a94e5155faf857de37b
timestamps:
  created: '2024-01-19T12:10:00Z'
  modified: '2024-01-19T12:24:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 430c7a97fc59da5869d433f54922e566
  status: accepted
relations:
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [159, 201]
        quote: 'Reminder: Capacity planning closes Friday.'
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [22, 66]
        quote: 'Reminder: Employee onboarding closes Friday.'
---

**Sam Kaur** (12:10): Reminder: Employee onboarding closes Friday.

**Sam Kaur** (12:17): Reminder: Employee onboarding closes Friday.

**Ana Brito** (12:24): Reminder: Capacity planning closes Friday.
