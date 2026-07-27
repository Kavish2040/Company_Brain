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
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 7ec13d3b4a4546b18500190f38c3966f
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
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [140, 229]
        quote: 3 escalations were handed to Engineering this week; 0 bounced back to Support unresolved.
  - predicate: mentions
    object: accounts/support-inbox
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [0, 53]
        quote: '**From:** Meridian Support <support@meridian.example>'
  - predicate: mentions
    object: people/dev-oyelaran
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [55, 83]
        quote: '**To:** dev@meridian.example'
  - predicate: mentions
    object: processes/customer-escalation
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [140, 229]
        quote: 3 escalations were handed to Engineering this week; 0 bounced back to Support unresolved.
  - predicate: mentions
    object: teams/support
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [140, 229]
        quote: 3 escalations were handed to Engineering this week; 0 bounced back to Support unresolved.
---

**From:** Meridian Support <support@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-01-28T11:00:00+00:00

Automated digest. 3 escalations were handed to Engineering this week; 0 bounced back to Support unresolved.
