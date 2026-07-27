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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 5c7c7e86e298bb70eaca9e4d99fe60ed
  status: accepted
relations:
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [61, 123]
        quote: This policy governs customer escalation at Meridian Logistics.
  - predicate: mentions
    object: teams/support
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [47, 60]
        quote: 'Team: Support'
  - predicate: owns
    subject: people/dev-oyelaran
    object: processes/customer-escalation
    confidence: 0.9
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
