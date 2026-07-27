---
id: documents/docs/processes/employee-onboarding-d32ded
type: Document
title: Employee onboarding
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/processes/onboarding.md
  external_id: docs/processes/onboarding.md
  external_version: 1095ed81285fd97e
  content_sha256: 1095ed81285fd97ec06f0d921d1c86cec94d9f84e33cfe633a38f8c7fb68f22d
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 47955c9304421c7d930a31463c33e8bc
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/product
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [465, 527]
        quote: Product hands off to Finance when a cost approval is required.
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [530, 603]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: mentions
    object: teams/product
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [67, 84]
        quote: '**Team:** Product'
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [240, 271]
        quote: Request is raised in PagerDuty.
  - predicate: owns
    subject: people/zoe-ravel
    object: processes/onboarding
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [23, 66]
        quote: '**Owner:** Zoë Ravel (zoe@meridian.example)'
---

# Employee onboarding

**Owner:** Zoë Ravel (zoe@meridian.example)
**Team:** Product

## Purpose

The employee onboarding process governs how Meridian handles employee onboarding requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in PagerDuty.
2. Product triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. Zoë Ravel signs off before the request is closed.

## Handoffs

- Product hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
