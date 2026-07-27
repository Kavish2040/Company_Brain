---
id: documents/docs/meetings/customer-escalation-sync-2024-02-23-1bfb60
type: Document
title: Customer escalation sync — 2024-02-23
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-23-customer-escalation.md
  external_id: docs/meetings/2024-02-23-customer-escalation.md
  external_version: 3065447de8dda128
  content_sha256: 3065447de8dda1286ca7e81acb36c33bb4f319e03a2b566ea6fdd00326eb97af
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 3f23081ed86bfb750d42e4f4c8057db2
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [86, 95]
        quote: Ana Brito
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [195, 207]
        quote: Dev Oyelaran
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [69, 84]
        quote: Owen Fitzgerald
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
        span: [97, 105]
        quote: Sam Kaur
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
        span: [255, 266]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [270, 277]
        quote: Finance
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [184, 191]
        quote: Datadog
---

# Customer escalation sync — 2024-02-23

**Attendees:** Priya Raman, Owen Fitzgerald, Ana Brito, Sam Kaur

## Notes

- Priya Raman raised that customer escalation is still blocked on
 Datadog.
- Dev Oyelaran confirmed they own the process.
- Handoff from Engineering to Finance is unclear; two
 tickets bounced back last week.

## Actions

- Sam Kaur to document the handoff boundary.
