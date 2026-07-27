---
id: documents/docx/release-sign-off-runbook-757499
type: Document
title: Release sign-off runbook
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docx/release-signoff-runbook.docx
  external_id: docx/release-signoff-runbook.docx
  external_version: c797fc18c39832ed
  content_sha256: c797fc18c39832edbb69e7a473fe81053ac07e81be8680fae948e5bd8d42b1ab
authors:
  - people/priya-raman
timestamps:
  created: '2024-01-20T09:00:00Z'
  modified: '2024-01-21T09:00:00Z'
normalizer:
  name: docx
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 315317689f48df71e241b0b9d109bde3
  status: accepted
relations:
  - predicate: authored_by
    object: people/priya-raman
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [50, 72]
        quote: priya@meridian.example
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 18]
        quote: Release sign-off
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [88, 99]
        quote: Engineering
  - predicate: owns
    object: people/priya-raman
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [30, 49]
        quote: 'Owner: Priya Raman'
---

# Release sign-off — runbook

Owner: Priya Raman (priya@meridian.example)

Owning team: Engineering

## Escalation path

- Engineering triage

- Cross-team handoff if root cause sits elsewhere

- Sign-off by Priya Raman

| Stage | Owner |

| --- | --- |

| Triage | Engineering |

| Sign-off | Priya Raman |
