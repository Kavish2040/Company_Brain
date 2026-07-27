---
id: documents/slack/leadership-comp/slack-thread-2024-01-08-fd51ee
type: Document
title: Slack thread — 2024-01-08
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-08.json
  external_id: slack/leadership-comp/2024-01-08.json
  external_version: 2246c366340b6e72
  content_sha256: 2246c366340b6e72d6b36e3722acbc2e81b2eff83342d66add52c4ab1e8d87e4
timestamps:
  created: '2024-01-08T14:13:00Z'
  modified: '2024-01-08T14:20:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: b7ca096f7012372bc655f3cbf7896a8b
  status: accepted
relations:
  - predicate: mentions
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [25, 97]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
---

**Priya Raman** (14:13): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (14:20): Compensation bands for the Engineering ladder need revisiting before Q3.
