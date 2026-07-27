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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: ed4327bb104bcb42f59e6d754bd3fa56
  status: accepted
relations:
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [32, 47]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [0, 17]
        quote: Incident response
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [54, 65]
        quote: Engineering
  - predicate: owns
    subject: people/owen-fitz
    object: processes/incident-response
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [25, 47]
        quote: 'Owner: Owen Fitzgerald'
---

Incident response Policy
Owner: Owen Fitzgerald
Team: Engineering
This policy governs incident response at Meridian Logistics.
Approvals must be recorded before closure.
Reviewed 2024-01-13.
