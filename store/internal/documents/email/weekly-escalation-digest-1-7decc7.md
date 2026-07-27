---
id: documents/email/weekly-escalation-digest-1-7decc7
type: Document
title: Weekly escalation digest 1
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/digest-000.eml
  external_id: email/digest-000.eml
  external_version: 2a2c98cd7ab64aba
  content_sha256: 2a2c98cd7ab64abaf83b0698f332ec29880f98731996b5c05e823d4e55c22d83
authors:
  - accounts/support-inbox
  - people/dev-oyelaran
timestamps:
  created: &id001 '2024-01-28T11:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: b659f3d3e76cf9487c0885a7eb5af2c2
  status: accepted
relations:
  - predicate: authored_by
    object: accounts/support-inbox
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/dev-oyelaran
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: accounts/support-inbox
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [28, 52]
        quote: support@meridian.example
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [63, 83]
        quote: dev@meridian.example
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [169, 180]
        quote: Engineering
  - predicate: mentions
    object: teams/support
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [210, 217]
        quote: Support
---

**From:** Meridian Support <support@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-01-28T11:00:00+00:00

Automated digest. 3 escalations were handed to Engineering this week; 0 bounced back to Support unresolved.
