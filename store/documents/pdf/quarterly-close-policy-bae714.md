---
id: documents/pdf/quarterly-close-policy-bae714
type: Document
title: Quarterly close Policy
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/pdf/quarterly-close-policy.pdf
  external_id: pdf/quarterly-close-policy.pdf
  external_version: ffe47f6174e3c6fd
  content_sha256: ffe47f6174e3c6fd8ae0093ef373a0044c929ba93baad2c27d9376bc8ce65fd0
normalizer:
  name: pdf
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 21254d3bf53d11af830ba8e8250f6e64
  status: accepted
relations:
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [54, 112]
        quote: This policy governs quarterly close at Meridian Logistics.
  - predicate: mentions
    object: teams/finance
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [40, 53]
        quote: 'Team: Finance'
  - predicate: owns
    object: people/ana-brito
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [23, 39]
        quote: 'Owner: Ana Brito'
---

Quarterly close Policy
Owner: Ana Brito
Team: Finance
This policy governs quarterly close at Meridian Logistics.
Approvals must be recorded before closure.
Reviewed 2024-01-23.
