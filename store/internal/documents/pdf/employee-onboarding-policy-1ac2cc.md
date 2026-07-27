---
id: documents/pdf/employee-onboarding-policy-1ac2cc
type: Document
title: Employee onboarding Policy
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/pdf/onboarding-policy.pdf
  external_id: pdf/onboarding-policy.pdf
  external_version: 6bf1b1e48fb1d264
  content_sha256: 6bf1b1e48fb1d26497a1e214bbcb13d1e9bd31852270d50b336689066281f1f7
normalizer:
  name: pdf
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 26c3831f0afb7b6d4e6082268e03b0c1
  status: accepted
relations:
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [58, 120]
        quote: This policy governs employee onboarding at Meridian Logistics.
  - predicate: mentions
    object: teams/product
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [44, 57]
        quote: 'Team: Product'
---

Employee onboarding Policy
Owner: Zo? Ravel
Team: Product
This policy governs employee onboarding at Meridian Logistics.
Approvals must be recorded before closure.
Reviewed 2024-02-02.
