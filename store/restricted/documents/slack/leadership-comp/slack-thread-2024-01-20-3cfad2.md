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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: ff5546d0f1e17e8af292b621ebe27dd8
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [98, 173]
        quote: 'Priya Raman** (11:13): Let''s keep the comp discussion in this channel only.'
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [2, 94]
        quote: 'Sam Kaur** (11:06): Compensation bands for the Engineering ladder need revisiting before Q3.'
  - predicate: mentions
    object: teams/engineering
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [22, 94]
        quote: Compensation bands for the Engineering ladder need revisiting before Q3.
---

**Sam Kaur** (11:06): Compensation bands for the Engineering ladder need revisiting before Q3.

**Priya Raman** (11:13): Let's keep the comp discussion in this channel only.

**Sam Kaur** (11:20): Compensation bands for the Engineering ladder need revisiting before Q3.
