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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 0308c8f095626ef29b19df3f5bc5ece4
  status: accepted
relations:
  - predicate: authored_by
    object: people/owen-fitz
    confidence: 1.0
    provenance: structural
    status: accepted
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
