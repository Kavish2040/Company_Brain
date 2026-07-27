---
id: documents/docs/meetings/customer-escalation-sync-2024-02-03-dd04c9
type: Document
title: Customer escalation sync — 2024-02-03
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-03-customer-escalation.md
  external_id: docs/meetings/2024-02-03-customer-escalation.md
  external_version: abe4383b3985e153
  content_sha256: abe4383b3985e15355480f0f06e1b65dbaa18a7d76ecbdcf09720fffa89ba296
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: c6592220ca7b27de6b874b24cdc32e47
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [90, 99]
        quote: Ana Brito
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [189, 201]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [56, 67]
        quote: Priya Raman
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [80, 88]
        quote: Sam Kaur
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [69, 78]
        quote: Zoë Ravel
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
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [260, 267]
        quote: Finance
  - predicate: mentions
    object: teams/product
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [249, 256]
        quote: Product
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [178, 185]
        quote: Datadog
---

# Customer escalation sync — 2024-02-03

**Attendees:** Priya Raman, Zoë Ravel, Sam Kaur, Ana Brito

## Notes

- Priya Raman raised that customer escalation is still blocked on
 Datadog.
- Dev Oyelaran confirmed they own the process.
- Handoff from Product to Finance is unclear; two
 tickets bounced back last week.

## Actions

- Ana Brito to document the handoff boundary.
