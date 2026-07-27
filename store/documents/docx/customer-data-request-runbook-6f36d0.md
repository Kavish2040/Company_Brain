---
id: documents/docx/customer-data-request-runbook-6f36d0
type: Document
title: Customer data request runbook
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docx/data-request-runbook.docx
  external_id: docx/data-request-runbook.docx
  external_version: 921ff51e7a4070af
  content_sha256: 921ff51e7a4070afbaec62e7dfdc092df13661ec3527fe7e2dbe541b19273416
authors:
  - people/mei-tanaka
timestamps:
  created: '2024-02-04T09:00:00Z'
  modified: '2024-02-05T09:00:00Z'
normalizer:
  name: docx
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 55165646c0cb98e0ffea608beb215437
  status: accepted
relations:
  - predicate: authored_by
    object: people/mei-tanaka
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [190, 212]
        quote: Sign-off by Mei Tanaka
  - predicate: mentions
    object: processes/data-request
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [0, 33]
        quote: '# Customer data request — runbook'
  - predicate: mentions
    object: teams/support
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [250, 266]
        quote: Triage | Support
  - predicate: owns
    object: people/mei-tanaka
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [35, 75]
        quote: 'Owner: Mei Tanaka (mei@meridian.example)'
  - predicate: owns
    object: teams/support
    confidence: 0.95
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [77, 97]
        quote: 'Owning team: Support'
---

# Customer data request — runbook

Owner: Mei Tanaka (mei@meridian.example)

Owning team: Support

## Escalation path

- Support triage

- Cross-team handoff if root cause sits elsewhere

- Sign-off by Mei Tanaka

| Stage | Owner |

| --- | --- |

| Triage | Support |

| Sign-off | Mei Tanaka |
