---
id: documents/docs/processes/customer-data-request-530ca5
type: Document
title: Customer data request
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/processes/data-request.md
  external_id: docs/processes/data-request.md
  external_version: 0e004561563b8913
  content_sha256: 0e004561563b8913c0a1a8bf835526ae5774ceea27bac2ad2be5e55dd5410002
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 30ceee79f132347f238649e71049a74b
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
        span: [536, 568]
        quote: Support hands off to Engineering
  - predicate: handoff_to
    subject: teams/support
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [471, 499]
        quote: Support hands off to Finance
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [48, 68]
        quote: mei@meridian.example
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 23]
        quote: Customer data request
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [557, 568]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [492, 499]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [594, 601]
        quote: product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [80, 87]
        quote: Support
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [268, 275]
        quote: Zendesk
---

# Customer data request

**Owner:** Mei Tanaka (mei@meridian.example)
**Team:** Support

## Purpose

The customer data request process governs how Meridian handles customer data request requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in Zendesk.
2. Support triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. Mei Tanaka signs off before the request is closed.

## Handoffs

- Support hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
