---
id: documents/email/weekly-escalation-digest-2-8e9861
type: Document
title: Weekly escalation digest 2
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/digest-001.eml
  external_id: email/digest-001.eml
  external_version: 7f7dcff379e18246
  content_sha256: 7f7dcff379e18246ad60e1ab64b8d1aad5ec3ca0d3fbd96be9394481dcc0b2ca
authors:
  - accounts/support-inbox
  - people/dev-oyelaran
timestamps:
  created: &id001 '2024-01-29T11:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 08c505d88eb75281619a817e577f6626
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
    object: processes/customer-escalation
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [140, 229]
        quote: 4 escalations were handed to Engineering this week; 1 bounced back to Support unresolved.
  - predicate: mentions
    object: teams/engineering
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [140, 229]
        quote: 4 escalations were handed to Engineering this week; 1 bounced back to Support unresolved.
---

**From:** Meridian Support <support@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-01-29T11:00:00+00:00

Automated digest. 4 escalations were handed to Engineering this week; 1 bounced back to Support unresolved.
