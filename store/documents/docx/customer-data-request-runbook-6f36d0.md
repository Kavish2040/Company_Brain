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
  prompt_version: claude-roster-v2
  cache_key: a699b5f5ef18c83f02f3fedad0512472
  status: accepted
relations:
  - predicate: authored_by
    object: people/mei-tanaka
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: owns
    subject: teams/support
    object: processes/data-request
    confidence: 0.9
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
