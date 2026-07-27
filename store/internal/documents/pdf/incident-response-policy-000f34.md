---
id: documents/pdf/incident-response-policy-000f34
type: Document
title: Incident response Policy
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/pdf/incident-response-policy.pdf
  external_id: pdf/incident-response-policy.pdf
  external_version: e68ad7c3669b01a4
  content_sha256: e68ad7c3669b01a418b537abf74ea6a8ca28605c95388b33da2edbcb830b6d79
normalizer:
  name: pdf
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: c2089d08a327db57f3535310d0654fce
  status: accepted
relations:
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.95
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [66, 126]
        quote: This policy governs incident response at Meridian Logistics.
  - predicate: owns
    subject: teams/engineering
    object: processes/incident-response
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [48, 65]
        quote: 'Team: Engineering'
---

Incident response Policy
Owner: Owen Fitzgerald
Team: Engineering
This policy governs incident response at Meridian Logistics.
Approvals must be recorded before closure.
Reviewed 2024-01-13.
