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
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 393d95434cb40e2edb419fdb01007945
  status: accepted
relations:
  - predicate: authored_by
    object: people/sam-kaur
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [45, 70]
        quote: sam.kaur@meridian.example
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 16]
        quote: Vendor renewal
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [86, 93]
        quote: Finance
  - predicate: owns
    subject: people/sam-kaur
    object: processes/vendor-renewal
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [28, 44]
        quote: 'Owner: Sam Kaur'
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
