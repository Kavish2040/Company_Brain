---
id: documents/slack/leadership-comp/slack-thread-2024-01-20-3cfad2
type: Document
title: Slack thread — 2024-01-20
status: active
acl:
  ref: slack:channel:C0LEAD
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/leadership-comp/2024-01-20.json
  external_id: slack/leadership-comp/2024-01-20.json
  external_version: 169624f4dac21250
  content_sha256: 169624f4dac212503f8bcf7859bb5b8ee44ffe231ddc02b5e77fcdd3e8ba2987
timestamps:
  created: '2024-01-20T11:06:00Z'
  modified: '2024-01-20T11:20:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: b4e89cba3b436f1cdd2ef27074e596a9
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [98, 109]
        quote: Priya Raman
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
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [49, 60]
        quote: Engineering
---

**Sam Kaur** (11:06): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (11:13): Let's keep the comp discussion in this channel only.

**Sam Kaur** (11:20): Compensation bands for the Engineering ladder need revisiting before Q3.
