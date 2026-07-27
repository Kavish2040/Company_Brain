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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: df42072b15c449d4866222c93b32c822
  status: accepted
relations:
  - predicate: handoff_to
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [549, 622]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: handoff_to
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [480, 546]
        quote: Engineering hands off to Finance when a cost approval is required.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [72, 93]
        quote: '**Team:** Engineering'
  - predicate: mentions
    object: tools/pagerduty
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [245, 276]
        quote: Request is raised in PagerDuty.
  - predicate: owns
    object: people/owen-fitz
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [408, 463]
        quote: Owen Fitzgerald signs off before the request is closed.
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
