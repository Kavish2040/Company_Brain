---
id: documents/docx/quarterly-close-runbook-6ad20a
type: Document
title: Quarterly close runbook
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docx/quarterly-close-runbook.docx
  external_id: docx/quarterly-close-runbook.docx
  external_version: 4f21309f0fb0b8a7
  content_sha256: 4f21309f0fb0b8a75f616e4824540047f5a853578d4f9526dcc3c3751a45fc29
authors:
  - people/ana-brito
timestamps:
  created: '2024-01-17T09:00:00Z'
  modified: '2024-01-18T09:00:00Z'
normalizer:
  name: docx
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 492ee57be4daab1fcaa14509145b629d
  status: accepted
relations:
  - predicate: authored_by
    object: people/ana-brito
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: owns
    object: people/ana-brito
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [29, 68]
        quote: 'Owner: Ana Brito (ana@meridian.example)'
  - predicate: owns
    object: teams/finance
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [70, 90]
        quote: 'Owning team: Finance'
---

# Quarterly close — runbook

Owner: Ana Brito (ana@meridian.example)

Owning team: Finance

## Escalation path

- Finance triage

- Cross-team handoff if root cause sits elsewhere

- Sign-off by Ana Brito

| Stage | Owner |

| --- | --- |

| Triage | Finance |

| Sign-off | Ana Brito |
