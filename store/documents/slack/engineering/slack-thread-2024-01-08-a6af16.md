---
id: documents/slack/engineering/slack-thread-2024-01-08-a6af16
type: Document
title: Slack thread — 2024-01-08
status: active
acl:
  ref: slack:channel:C0ENG
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/engineering/2024-01-08.json
  external_id: slack/engineering/2024-01-08.json
  external_version: bfb0164dce979ff3
  content_sha256: bfb0164dce979ff3b40f7c161eb58b46c2c5cda5b5d082646e7ac3a312718605
timestamps:
  created: '2024-01-08T12:55:00Z'
  modified: '2024-01-08T13:02:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 5ab55fcdbc64270fa0c703a45d278640
  status: accepted
relations:
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [105, 115]
        quote: Tom Whelan
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 11]
        quote: Zoë Ravel
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [38, 55]
        quote: Incident response
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [84, 100]
        quote: release sign-off
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [131, 139]
        quote: NetSuite
---

**Zoë Ravel** (12:55): Deploy for the Incident response change is queued behind the release sign-off.

**Tom Whelan** (13:02): The NetSuite alert fired again overnight — third time this week.
