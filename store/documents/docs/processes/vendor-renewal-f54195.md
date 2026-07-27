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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 2ea2dd32859e7aa83337d72929ee31cd
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
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [39, 64]
        quote: sam.kaur@meridian.example
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 16]
        quote: Vendor renewal
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
        span: [76, 83]
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
        span: [250, 257]
        quote: Datadog
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
