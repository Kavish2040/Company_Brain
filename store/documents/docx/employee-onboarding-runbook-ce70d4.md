---
id: documents/docx/employee-onboarding-runbook-ce70d4
type: Document
title: Employee onboarding runbook
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docx/onboarding-runbook.docx
  external_id: docx/onboarding-runbook.docx
  external_version: 46bc2a0825addbfe
  content_sha256: 46bc2a0825addbfe9256932404aa956a69b0196cae9536136f513a31666b8768
authors:
  - people/zoe-ravel
timestamps:
  created: '2024-01-23T09:00:00Z'
  modified: '2024-01-24T09:00:00Z'
normalizer:
  name: docx
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: dbcd9bc18d72d1ad4aee03094f494da2
  status: accepted
relations:
  - predicate: authored_by
    object: people/zoe-ravel
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: owns
    subject: teams/product
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [74, 94]
        quote: 'Owning team: Product'
---

# Employee onboarding — runbook

Owner: Zoë Ravel (zoe@meridian.example)

Owning team: Product

## Escalation path

- Product triage

- Cross-team handoff if root cause sits elsewhere

- Sign-off by Zoë Ravel

| Stage | Owner |

| --- | --- |

| Triage | Product |

| Sign-off | Zoë Ravel |
