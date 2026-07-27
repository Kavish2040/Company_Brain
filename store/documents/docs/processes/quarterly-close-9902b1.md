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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 7197f2dfccdd18395078477aba9d6228
  status: accepted
relations:
  - predicate: handoff_to
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [516, 548]
        quote: Support hands off to Engineering
  - predicate: handoff_to
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [451, 479]
        quote: Finance hands off to Finance
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [41, 61]
        quote: ana@meridian.example
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Quarterly close
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [537, 548]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [73, 80]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [574, 581]
        quote: product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [516, 523]
        quote: Support
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [249, 256]
        quote: Datadog
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
