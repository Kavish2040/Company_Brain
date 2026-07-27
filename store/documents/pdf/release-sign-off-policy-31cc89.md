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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: dadc0484a40b17006b7d54d8af829030
  status: accepted
relations:
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [61, 120]
        quote: This policy governs release sign-off at Meridian Logistics.
  - predicate: owns
    object: people/priya-raman
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [24, 42]
        quote: 'Owner: Priya Raman'
  - predicate: owns
    object: teams/engineering
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [43, 60]
        quote: 'Team: Engineering'
---

Release sign-off Policy
Owner: Priya Raman
Team: Engineering
This policy governs release sign-off at Meridian Logistics.
Approvals must be recorded before closure.
Reviewed 2024-01-28.
