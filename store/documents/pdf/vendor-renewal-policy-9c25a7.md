---
id: documents/pdf/vendor-renewal-policy-9c25a7
type: Document
title: Vendor renewal Policy
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/pdf/vendor-renewal-policy.pdf
  external_id: pdf/vendor-renewal-policy.pdf
  external_version: 27245571af99cc56
  content_sha256: 27245571af99cc565a3b5cca727faa014108dfe31af97181e3fb67f50b2faa35
normalizer:
  name: pdf
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: caf9cd3535ce659a4c66f5fd339e65af
  status: accepted
relations:
  - predicate: mentions
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [38, 51]
        quote: 'Team: Finance'
  - predicate: owns
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [22, 37]
        quote: 'Owner: Sam Kaur'
---

Vendor renewal Policy
Owner: Sam Kaur
Team: Finance
This policy governs vendor renewal at Meridian Logistics.
Approvals must be recorded before closure.
Reviewed 2024-01-08.
