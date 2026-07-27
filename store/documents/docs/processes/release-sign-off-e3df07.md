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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 79de994c8a7ecfb30302961ebd8f1b8c
  status: accepted
relations:
  - predicate: handoff_to
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [537, 569]
        quote: Support hands off to Engineering
  - predicate: handoff_to
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [468, 500]
        quote: Engineering hands off to Finance
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [44, 66]
        quote: priya@meridian.example
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 18]
        quote: Release sign-off
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [78, 89]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [493, 500]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [595, 602]
        quote: product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [537, 544]
        quote: Support
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [260, 267]
        quote: Datadog
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
