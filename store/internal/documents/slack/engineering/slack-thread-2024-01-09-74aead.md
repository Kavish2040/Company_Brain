---
id: documents/slack/engineering/slack-thread-2024-01-09-74aead
type: Document
title: Slack thread — 2024-01-09
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-09.json
  external_id: slack/engineering/2024-01-09.json
  external_version: 5fee6f2ed349dae4
  content_sha256: 5fee6f2ed349dae48d8a1ec5e5db257c7c860365052a2279a575c011cdb2ab3d
timestamps:
  created: '2024-01-09T14:28:00Z'
  modified: '2024-01-09T14:35:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 83df5cc1f2ad518f44b411295247a90e
  status: accepted
relations:
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 14]
        quote: Nadia Hassan
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [89, 100]
        quote: Priya Raman
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [43, 50]
        quote: Finance
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [63, 71]
        quote: NetSuite
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [149, 158]
        quote: Snowflake
---

**Nadia Hassan** (14:28): Can someone from Finance confirm the NetSuite renewal date?

**Priya Raman** (14:35): Can someone from Finance confirm the Snowflake renewal date?
