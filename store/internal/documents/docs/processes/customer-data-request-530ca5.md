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
  prompt_version: claude-roster-v2
  cache_key: 2b463bcb823496835cf4682fba5b1c52
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [536, 609]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: handoff_to
    subject: teams/support
    object: teams/finance
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [471, 533]
        quote: Support hands off to Finance when a cost approval is required.
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [404, 454]
        quote: Mei Tanaka signs off before the request is closed.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [628, 730]
        quote: 'Tickets frequently bounce between Support and Engineering when ownership of the

          root cause is unclear.'
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [247, 276]
        quote: Request is raised in Zendesk.
  - predicate: owns
    subject: teams/support
    object: processes/data-request
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
