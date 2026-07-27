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
  prompt_version: claude-roster-v2
  cache_key: 5a8f79e771d99c12bb92e84cd7dc6318
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
  - predicate: mentions
    object: teams/engineering
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [43, 60]
        quote: 'Team: Engineering'
  - predicate: owns
    subject: people/priya-raman
    object: processes/release-signoff
    confidence: 0.95
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
