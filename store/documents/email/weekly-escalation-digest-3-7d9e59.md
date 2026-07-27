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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 7e9ff17f7b308354d6fc0b5037aa7fbb
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
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [159, 180]
        quote: handed to Engineering
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

**Date:** 2024-01-30T11:00:00+00:00

Automated digest. 5 escalations were handed to Engineering this week; 2 bounced back to Support unresolved.
