---
id: documents/docs/processes/vendor-renewal-f54195
type: Document
title: Vendor renewal
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/processes/vendor-renewal.md
  external_id: docs/processes/vendor-renewal.md
  external_version: 6387cac41ee9d898
  content_sha256: 6387cac41ee9d89868b1ffc5dddefbf5611becc97a9daeef8c4a4e24e281343e
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: b1b6d108023c91250b15034c476fcc28
  status: accepted
relations:
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [516, 589]
        quote: Support hands off to Engineering when the root cause is a product defect.
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [386, 434]
        quote: Sam Kaur signs off before the request is closed.
  - predicate: mentions
    object: teams/finance
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [66, 83]
        quote: '**Team:** Finance'
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [229, 258]
        quote: Request is raised in Datadog.
  - predicate: owns
    subject: people/sam-kaur
    object: processes/vendor-renewal
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [18, 65]
        quote: '**Owner:** Sam Kaur (sam.kaur@meridian.example)'
---

# Vendor renewal

**Owner:** Sam Kaur (sam.kaur@meridian.example)
**Team:** Finance

## Purpose

The vendor renewal process governs how Meridian handles vendor renewal requests
end to end. It is reviewed quarterly.

## Steps

1. Request is raised in Datadog.
2. Finance triages within one business day.
3. If the request crosses team boundaries, it is handed off to the owning team.
4. Sam Kaur signs off before the request is closed.

## Handoffs

- Finance hands off to Finance when a cost approval is required.
- Support hands off to Engineering when the root cause is a product defect.

## Known issues

Tickets frequently bounce between Support and Engineering when ownership of the
root cause is unclear.
