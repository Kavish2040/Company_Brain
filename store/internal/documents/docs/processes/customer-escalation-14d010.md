---
id: documents/docs/processes/customer-escalation-14d010
type: Document
title: Customer escalation
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/processes/customer-escalation.md
  external_id: docs/processes/customer-escalation.md
  external_version: 4056a52bb3ce6606
  content_sha256: 4056a52bb3ce660639677c03541e00002a8fea667a63b90ad1e49be579c8759d
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: e86803a17229eb4a69a697a3e99146a8
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [534, 566]
        quote: Support hands off to Engineering
  - predicate: handoff_to
    subject: teams/support
    object: teams/finance
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [469, 497]
        quote: Support hands off to Finance
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [48, 68]
        quote: dev@meridian.example
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 21]
        quote: Customer escalation
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [555, 566]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [490, 497]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [592, 599]
        quote: product
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [80, 87]
        quote: Support
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [264, 271]
        quote: Zendesk
---

# Customer escalation

**Owner:** Dev Oyelaran (dev@meridian.example)
**Team:** Support

## Purpose

The customer escalation process governs how Meridian handles customer escalation requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in Zendesk.
2. Support triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. Dev Oyelaran signs off before the request is closed.

## Handoffs

- Support hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
