---
id: documents/slack/leadership-comp/slack-thread-2024-01-08-fd51ee
type: Document
title: Slack thread — 2024-01-08
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: slack
  uri: file://corpus/slack/leadership-comp/2024-01-08.json
  external_id: leadership-comp/2024-01-08
  external_version: rev-0
  content_sha256: 2246c366340b6e72d6b36e3722acbc2e81b2eff83342d66add52c4ab1e8d87e4
timestamps:
  created: '2024-01-08T14:13:00Z'
  modified: '2024-01-08T14:20:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 16e3e918b5ad18cafc1de7981ea08066
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 13]
        quote: Priya Raman
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [52, 63]
        quote: Engineering
---

**Priya Raman** (14:13): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (14:20): Compensation bands for the Engineering ladder need revisiting before Q3.
