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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 7ce1ce54d431b5822aee8be2fbe8b373
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/product
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [465, 493]
        quote: Product hands off to Finance
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [530, 562]
        quote: Support hands off to Engineering
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [45, 65]
        quote: zoe@meridian.example
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 21]
        quote: Employee onboarding
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [551, 562]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [486, 493]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [77, 84]
        quote: Product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [530, 537]
        quote: Support
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [261, 270]
        quote: PagerDuty
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
