---
id: documents/docs/processes/capacity-planning-69a4cb
type: Document
title: Capacity planning
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/processes/capacity-planning.md
  external_id: docs/processes/capacity-planning.md
  external_version: 9a531510bf3e0d15
  content_sha256: 9a531510bf3e0d1592b94f5c488b7ff3449e26b89466ed48e5692d97e42583e7
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: eb4113437e60badb7c9da5b4a8a07686
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/engineering
    object: teams/finance
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [478, 544]
        quote: Engineering hands off to Finance when a cost approval is required.
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [547, 620]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [245, 274]
        quote: Request is raised in Datadog.
  - predicate: owns
    subject: people/owen-fitz
    object: processes/capacity-planning
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [21, 71]
        quote: '**Owner:** Owen Fitzgerald (owen@meridian.example)'
---

# Capacity planning

**Owner:** Owen Fitzgerald (owen@meridian.example)
**Team:** Engineering

## Purpose

The capacity planning process governs how Meridian handles capacity planning requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in Datadog.
2. Engineering triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. Owen Fitzgerald signs off before the request is closed.

## Handoffs

- Engineering hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
