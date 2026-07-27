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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 27c70846f4f79cdf5abc47dddde40ab6
  status: accepted
relations:
  - predicate: owns
    object: people/mei-tanaka
    confidence: 0.97
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [25, 69]
        quote: '**Owner:** Mei Tanaka (mei@meridian.example)'
  - predicate: owns
    object: teams/support
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [70, 87]
        quote: '**Team:** Support'
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
