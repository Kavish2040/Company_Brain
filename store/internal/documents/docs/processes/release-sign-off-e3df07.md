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
  prompt_version: claude-roster-v2
  cache_key: 9f2b21016ca70c89a051982428f73c9e
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
        span: [468, 534]
        quote: Engineering hands off to Finance when a cost approval is required.
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [537, 610]
        quote: Support hands off to Engineering when the root cause is a product defect.
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
    subject: teams/engineering
    object: processes/release-signoff
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [68, 89]
        quote: '**Team:** Engineering'
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
