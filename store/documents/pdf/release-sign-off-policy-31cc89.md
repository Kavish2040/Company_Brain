---
id: documents/pdf/release-sign-off-policy-31cc89
type: Document
title: Release sign-off Policy
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/pdf/release-signoff-policy.pdf
  external_id: pdf/release-signoff-policy.pdf
  external_version: e75f36537b3e489d
  content_sha256: e75f36537b3e489d7347025bcb87e2ab3cbd4607a6b67ecd6621f6153e3e4885
normalizer:
  name: pdf
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 19c2ccff8b6c206b113ca3f78f3fc06b
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [31, 42]
        quote: Priya Raman
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [0, 16]
        quote: Release sign-off
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [49, 60]
        quote: Engineering
  - predicate: owns
    object: people/priya-raman
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [24, 42]
        quote: 'Owner: Priya Raman'
---

Release sign-off Policy
Owner: Priya Raman
Team: Engineering
This policy governs release sign-off at Meridian Logistics.
Approvals must be recorded before closure.
Reviewed 2024-01-28.
