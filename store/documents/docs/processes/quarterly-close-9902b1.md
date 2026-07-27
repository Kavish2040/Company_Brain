---
id: documents/docs/processes/quarterly-close-9902b1
type: Document
title: Quarterly close
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/processes/quarterly-close.md
  external_id: docs/processes/quarterly-close.md
  external_version: 11158ea636b311a2
  content_sha256: 11158ea636b311a259089d3abf95f7eb6d35616cc5bd5c738300c1b449433611
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 902814b5ecf4c421c14bfb6218ac5669
  status: accepted
relations:
  - predicate: handoff_to
    object: teams/engineering
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [516, 589]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: handoff_to
    object: teams/finance
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [451, 513]
        quote: Finance hands off to Finance when a cost approval is required.
  - predicate: handoff_to
    object: teams/support
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [516, 589]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [385, 434]
        quote: Ana Brito signs off before the request is closed.
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [228, 257]
        quote: Request is raised in Datadog.
  - predicate: owns
    object: people/ana-brito
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [19, 62]
        quote: '**Owner:** Ana Brito (ana@meridian.example)'
  - predicate: owns
    object: teams/finance
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [63, 80]
        quote: '**Team:** Finance'
---

# Quarterly close

**Owner:** Ana Brito (ana@meridian.example)
**Team:** Finance

## Purpose

The quarterly close process governs how Meridian handles quarterly close requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in Datadog.
2. Finance triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. Ana Brito signs off before the request is closed.

## Handoffs

- Finance hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
