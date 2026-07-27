---
id: documents/docs/processes/refund-approval-4d01e1
type: Document
title: Refund approval
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/processes/refund-approval.md
  external_id: docs/processes/refund-approval.md
  external_version: 018e9c75683899b2
  content_sha256: 018e9c75683899b2ae32a8fb49fe25f687ee311fb01aef77cf3746131422e578
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 8a08fa6a7e08d70a0c182723cc2f5ff1
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [518, 550]
        quote: Support hands off to Engineering
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [41, 61]
        quote: ana@meridian.example
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Refund approval
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [539, 550]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [73, 80]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [576, 583]
        quote: product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [518, 525]
        quote: Support
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [249, 258]
        quote: PagerDuty
---

# Refund approval

**Owner:** Ana Brito (ana@meridian.example)
**Team:** Finance

## Purpose

The refund approval process governs how Meridian handles refund approval requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in PagerDuty.
2. Finance triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. Ana Brito signs off before the request is closed.

## Handoffs

- Finance hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
