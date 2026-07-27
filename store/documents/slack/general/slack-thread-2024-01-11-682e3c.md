---
id: documents/slack/general/slack-thread-2024-01-11-682e3c
type: Document
title: Slack thread — 2024-01-11
status: active
acl:
  ref: slack:channel:C0GEN
  sensitivity: public
source:
  connector: local_fs
  uri: file://corpus/slack/general/2024-01-11.json
  external_id: slack/general/2024-01-11.json
  external_version: 7b5176177e5cfd5c
  content_sha256: 7b5176177e5cfd5c05f75984000f66dd30e787c2e0530aa33b3315944c7b3a5f
timestamps:
  created: '2024-01-11T10:37:00Z'
  modified: '2024-01-11T10:44:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 68f6ab15ee741383390b55a0bb17a75c
  status: accepted
relations:
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 73]
        quote: Reminder that Quarterly close kicks off next week.
---

**Sam Kelly** (10:37): Reminder that Quarterly close kicks off next week.

**Priya Raman** (10:44): All-hands moved to Thursday.
