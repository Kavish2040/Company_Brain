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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 541b612ec871261a601d2601cef790c4
  status: accepted
relations:
  - predicate: authored_by
    object: people/ana-brito
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [47, 67]
        quote: ana@meridian.example
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Refund approval
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [83, 90]
        quote: Finance
  - predicate: owns
    subject: people/ana-brito
    object: processes/refund-approval
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [29, 46]
        quote: 'Owner: Ana Brito'
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
