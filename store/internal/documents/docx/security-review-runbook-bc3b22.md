---
id: documents/docx/security-review-runbook-bc3b22
type: Document
title: Security review runbook
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docx/security-review-runbook.docx
  external_id: docx/security-review-runbook.docx
  external_version: b28fd9cda29cff38
  content_sha256: b28fd9cda29cff38d1a833b8b2ab03d88368fe2f3fde1097c5437bc84f83f158
authors:
  - people/tom-whelan
timestamps:
  created: '2024-01-26T09:00:00Z'
  modified: '2024-01-27T09:00:00Z'
normalizer:
  name: docx
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 867ba90b2eca2356300b758c1b1ee00a
  status: accepted
relations:
  - predicate: authored_by
    object: people/tom-whelan
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [48, 68]
        quote: tom@meridian.example
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [84, 95]
        quote: Engineering
  - predicate: owns
    subject: people/tom-whelan
    object: processes/security-review
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [29, 47]
        quote: 'Owner: Tom Whelan'
---

# Security review — runbook

Owner: Tom Whelan (tom@meridian.example)

Owning team: Engineering

## Escalation path

- Engineering triage

- Cross-team handoff if root cause sits elsewhere

- Sign-off by Tom Whelan

| Stage | Owner |

| --- | --- |

| Triage | Engineering |

| Sign-off | Tom Whelan |
