---
id: documents/docs/processes/incident-response-82d460
type: Document
title: Incident response
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/processes/incident-response.md
  external_id: docs/processes/incident-response.md
  external_version: 75e81b6c30435537
  content_sha256: 75e81b6c30435537e27a02bfb195f8e54f5e4ddc71dc5df28ae0ac3eb2ae83a6
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 62be14947b298c0d1e3221b46142529d
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/engineering
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [480, 512]
        quote: Engineering hands off to Finance
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [549, 581]
        quote: Support hands off to Engineering
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [49, 70]
        quote: owen@meridian.example
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 19]
        quote: Incident response
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [82, 93]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [505, 512]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [607, 614]
        quote: product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [549, 556]
        quote: Support
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [266, 275]
        quote: PagerDuty
---

# Incident response

**Owner:** Owen Fitzgerald (owen@meridian.example)
**Team:** Engineering

## Purpose

The incident response process governs how Meridian handles incident response requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in PagerDuty.
2. Engineering triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. Owen Fitzgerald signs off before the request is closed.

## Handoffs

- Engineering hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
