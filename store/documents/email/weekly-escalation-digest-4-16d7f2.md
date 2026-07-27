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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 45f7539ea9b69bd9d69296b1626acfc0
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
  - predicate: handoff_to
    object: teams/engineering
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [140, 190]
        quote: 6 escalations were handed to Engineering this week
  - predicate: handoff_to
    object: teams/support
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [192, 228]
        quote: 3 bounced back to Support unresolved
  - predicate: mentions
    object: accounts/support-inbox
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [0, 53]
        quote: '**From:** Meridian Support <support@meridian.example>'
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [55, 83]
        quote: '**To:** dev@meridian.example'
---

**From:** Meridian Support <support@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-01-31T11:00:00+00:00

Automated digest. 6 escalations were handed to Engineering this week; 3 bounced back to Support unresolved.
