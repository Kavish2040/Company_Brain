---
id: documents/docx/incident-response-runbook-bfe75d
type: Document
title: Incident response runbook
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docx/incident-response-runbook.docx
  external_id: docx/incident-response-runbook.docx
  external_version: bc2fb52355ef8935
  content_sha256: bc2fb52355ef89358774d62359010ab60e90631c1fc2b60d5b56f423c5aba2a0
authors:
  - people/owen-fitz
timestamps:
  created: '2024-01-11T09:00:00Z'
  modified: '2024-01-12T09:00:00Z'
normalizer:
  name: docx
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: a6fca7770e6ce59853596ce3b53c6492
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
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 19]
        quote: Incident response
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
    object: people/owen-fitz
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [31, 54]
        quote: 'Owner: Owen Fitzgerald'
---

# Incident response — runbook

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
