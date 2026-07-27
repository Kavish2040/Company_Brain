---
id: documents/docs/processes/release-sign-off-e3df07
type: Document
title: Release sign-off
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/processes/release-signoff.md
  external_id: docs/processes/release-signoff.md
  external_version: f28dc306385e55b3
  content_sha256: f28dc306385e55b39a61f607db3ac1fbb3cf50673e300be6a82084dd664bbdf6
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: bf4375e94ddd2d7946fc307e40b09b4d
  status: accepted
relations:
  - predicate: handoff_to
    object: teams/engineering
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [537, 610]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: handoff_to
    object: teams/finance
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [468, 534]
        quote: Engineering hands off to Finance when a cost approval is required.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [68, 89]
        quote: '**Team:** Engineering'
  - predicate: mentions
    object: teams/support
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [629, 731]
        quote: 'Tickets frequently bounce between Support and Engineering when ownership of the

          root cause is unclear.'
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [239, 268]
        quote: Request is raised in Datadog.
  - predicate: owns
    object: people/priya-raman
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [20, 67]
        quote: '**Owner:** Priya Raman (priya@meridian.example)'
  - predicate: owns
    object: processes/release-signoff
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [400, 451]
        quote: Priya Raman signs off before the request is closed.
---

# Release sign-off

**Owner:** Priya Raman (priya@meridian.example)
**Team:** Engineering

## Purpose

The release sign-off process governs how Meridian handles release sign-off requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in Datadog.
2. Engineering triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. Priya Raman signs off before the request is closed.

## Handoffs

- Engineering hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
