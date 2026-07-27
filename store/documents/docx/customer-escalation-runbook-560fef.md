---
id: documents/docx/customer-escalation-runbook-560fef
type: Document
title: Customer escalation runbook
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docx/customer-escalation-runbook.docx
  external_id: docx/customer-escalation-runbook.docx
  external_version: 9f828087ab1f2f2f
  content_sha256: 9f828087ab1f2f2f49c6020414fc19b923391c671ac896c3666c5c7aff874bcf
authors:
  - people/dev-oyelaran
timestamps:
  created: '2024-01-14T09:00:00Z'
  modified: '2024-01-15T09:00:00Z'
normalizer:
  name: docx
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 6b6d49e295fdd453ce1425d6f674e69f
  status: accepted
relations:
  - predicate: authored_by
    object: people/dev-oyelaran
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [54, 74]
        quote: dev@meridian.example
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 21]
        quote: Customer escalation
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [90, 97]
        quote: Support
  - predicate: owns
    object: people/dev-oyelaran
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [33, 53]
        quote: 'Owner: Dev Oyelaran'
---

# Customer escalation — runbook

Owner: Dev Oyelaran (dev@meridian.example)

Owning team: Support

## Escalation path

- Support triage

- Cross-team handoff if root cause sits elsewhere

- Sign-off by Dev Oyelaran

| Stage | Owner |

| --- | --- |

| Triage | Support |

| Sign-off | Dev Oyelaran |
