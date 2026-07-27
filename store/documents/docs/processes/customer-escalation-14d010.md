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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 5dd8518dbee9ad38ce5c196883e59e08
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
        span: [534, 607]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: handoff_to
    subject: teams/support
    object: teams/finance
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [469, 531]
        quote: Support hands off to Finance when a cost approval is required.
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [400, 452]
        quote: Dev Oyelaran signs off before the request is closed.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [626, 728]
        quote: 'Tickets frequently bounce between Support and Engineering when ownership of the

          root cause is unclear.'
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [243, 272]
        quote: Request is raised in Zendesk.
  - predicate: owns
    subject: teams/support
    object: processes/customer-escalation
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [70, 87]
        quote: '**Team:** Support'
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
