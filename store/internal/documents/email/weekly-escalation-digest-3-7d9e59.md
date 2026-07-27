---
id: documents/email/weekly-escalation-digest-3-7d9e59
type: Document
title: Weekly escalation digest 3
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/digest-002.eml
  external_id: email/digest-002.eml
  external_version: 2cdb4ee5b979ddee
  content_sha256: 2cdb4ee5b979ddeeab283bd5dbd4797b0422e3c69d53f5bb48fe3eafd4ccb7c1
authors:
  - accounts/support-inbox
  - people/dev-oyelaran
timestamps:
  created: &id001 '2024-01-30T11:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 74376ad1037de00e37e1d445f9f474b5
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
    subject: teams/engineering
    object: teams/support
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [192, 229]
        quote: 2 bounced back to Support unresolved.
  - predicate: handoff_to
    subject: teams/support
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [140, 190]
        quote: 5 escalations were handed to Engineering this week
  - predicate: mentions
    object: accounts/support-inbox
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [10, 53]
        quote: Meridian Support <support@meridian.example>
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [63, 83]
        quote: dev@meridian.example
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.65
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [140, 229]
        quote: 5 escalations were handed to Engineering this week; 2 bounced back to Support unresolved.
---

**From:** Meridian Support <support@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-01-30T11:00:00+00:00

Automated digest. 5 escalations were handed to Engineering this week; 2 bounced back to Support unresolved.
