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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 721112f7a353c2537d272429574779c7
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [518, 591]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [387, 436]
        quote: Ana Brito signs off before the request is closed.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [610, 712]
        quote: 'Tickets frequently bounce between Support and Engineering when ownership of the

          root cause is unclear.'
  - predicate: mentions
    object: teams/finance
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [263, 303]
        quote: Finance triages within one business day.
  - predicate: mentions
    object: teams/support
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [610, 712]
        quote: 'Tickets frequently bounce between Support and Engineering when ownership of the

          root cause is unclear.'
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [228, 259]
        quote: Request is raised in PagerDuty.
  - predicate: owns
    subject: people/ana-brito
    object: processes/refund-approval
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [19, 62]
        quote: '**Owner:** Ana Brito (ana@meridian.example)'
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
