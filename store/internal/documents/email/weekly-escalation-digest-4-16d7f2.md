---
id: documents/email/weekly-escalation-digest-4-16d7f2
type: Document
title: Weekly escalation digest 4
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/digest-003.eml
  external_id: email/digest-003.eml
  external_version: 94b93a172128639b
  content_sha256: 94b93a172128639b0e08d89681a68c5852f20409b2d3b934a3928721f6734ae9
authors:
  - accounts/support-inbox
  - people/dev-oyelaran
timestamps:
  created: &id001 '2024-01-31T11:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: a28a755dab8de1bc4a28a308e03986fe
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

**Date:** 2024-01-31T11:00:00+00:00

Automated digest. 6 escalations were handed to Engineering this week; 3 bounced back to Support unresolved.
