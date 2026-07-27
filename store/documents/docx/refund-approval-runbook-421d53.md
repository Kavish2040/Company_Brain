---
id: documents/docx/refund-approval-runbook-421d53
type: Document
title: Refund approval runbook
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docx/refund-approval-runbook.docx
  external_id: docx/refund-approval-runbook.docx
  external_version: 673bfbdd9f953f09
  content_sha256: 673bfbdd9f953f097bc5ddcff2944f356028612512ba026bdbb40fcc732f6364
authors:
  - people/ana-brito
timestamps:
  created: '2024-02-01T09:00:00Z'
  modified: '2024-02-02T09:00:00Z'
normalizer:
  name: docx
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 64810a73a8558c715a301cc0575c9d43
  status: accepted
relations:
  - predicate: authored_by
    object: people/ana-brito
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: owns
    object: people/ana-brito
    confidence: 0.97
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

# Refund approval — runbook

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
