---
id: documents/docx/capacity-planning-runbook-3c39f6
type: Document
title: Capacity planning runbook
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docx/capacity-planning-runbook.docx
  external_id: docx/capacity-planning-runbook.docx
  external_version: febf34c162ce20d8
  content_sha256: febf34c162ce20d8368417b41495dd2cebc00e3f6a75ea739f989cf1572e9888
authors:
  - people/owen-fitz
timestamps:
  created: '2024-01-29T09:00:00Z'
  modified: '2024-01-30T09:00:00Z'
normalizer:
  name: docx
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 647e0fdb626d191cfd0d3d5814f500d5
  status: accepted
relations:
  - predicate: authored_by
    object: people/owen-fitz
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [55, 76]
        quote: owen@meridian.example
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 19]
        quote: Capacity planning
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [92, 103]
        quote: Engineering
  - predicate: owns
    subject: people/owen-fitz
    object: processes/capacity-planning
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [31, 54]
        quote: 'Owner: Owen Fitzgerald'
---

# Capacity planning — runbook

Owner: Owen Fitzgerald (owen@meridian.example)

Owning team: Engineering

## Escalation path

- Engineering triage

- Cross-team handoff if root cause sits elsewhere

- Sign-off by Owen Fitzgerald

| Stage | Owner |

| --- | --- |

| Triage | Engineering |

| Sign-off | Owen Fitzgerald |
