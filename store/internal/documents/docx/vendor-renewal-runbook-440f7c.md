---
id: documents/docx/vendor-renewal-runbook-440f7c
type: Document
title: Vendor renewal runbook
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docx/vendor-renewal-runbook.docx
  external_id: docx/vendor-renewal-runbook.docx
  external_version: af727032fb72eb87
  content_sha256: af727032fb72eb879ba70d32d48a7480f36a5f8c070c7703b440bb60669e2d69
authors:
  - people/sam-kaur
timestamps:
  created: '2024-01-08T09:00:00Z'
  modified: '2024-01-09T09:00:00Z'
normalizer:
  name: docx
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 30667c01dd34978a535dcf8be4f23f23
  status: accepted
relations:
  - predicate: authored_by
    object: people/sam-kaur
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [135, 182]
        quote: Cross-team handoff if root cause sits elsewhere
  - predicate: owns
    subject: teams/finance
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [73, 93]
        quote: 'Owning team: Finance'
---

# Vendor renewal — runbook

Owner: Sam Kaur (sam.kaur@meridian.example)

Owning team: Finance

## Escalation path

- Finance triage

- Cross-team handoff if root cause sits elsewhere

- Sign-off by Sam Kaur

| Stage | Owner |

| --- | --- |

| Triage | Finance |

| Sign-off | Sam Kaur |
