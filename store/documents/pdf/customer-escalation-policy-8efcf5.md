---
id: documents/pdf/customer-escalation-policy-8efcf5
type: Document
title: Customer escalation Policy
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/pdf/customer-escalation-policy.pdf
  external_id: pdf/customer-escalation-policy.pdf
  external_version: 60c1f288ba79ed14
  content_sha256: 60c1f288ba79ed14571923941acb2a9d70bfbb790461f4c64959dcc1f14bc6a1
normalizer:
  name: pdf
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 5c33c2387e3703ff1f2d27b8df067cda
  status: accepted
relations:
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [34, 46]
        quote: Dev Oyelaran
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [0, 19]
        quote: Customer escalation
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [53, 60]
        quote: Support
  - predicate: owns
    object: people/dev-oyelaran
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [27, 46]
        quote: 'Owner: Dev Oyelaran'
---

Customer escalation Policy
Owner: Dev Oyelaran
Team: Support
This policy governs customer escalation at Meridian Logistics.
Approvals must be recorded before closure.
Reviewed 2024-01-18.
