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
  prompt_version: claude-roster-v2
  cache_key: 6c6f47c05535848b394c6c87289bfcaf
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 39]
        quote: 'Owner: Ana Brito'
  - predicate: owns
    subject: teams/finance
    object: processes/quarterly-close
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [40, 53]
        quote: 'Team: Finance'
---

Quarterly close Policy
Owner: Ana Brito
Team: Finance
This policy governs quarterly close at Meridian Logistics.
Approvals must be recorded before closure.
Reviewed 2024-01-23.
