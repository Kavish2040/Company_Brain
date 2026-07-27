---
id: documents/email/re-quarterly-close-status-77fae3
type: Document
title: 'Re: Quarterly close ��� status'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-022.eml
  external_id: email/thread-022.eml
  external_version: 758e639eebfc83ea
  content_sha256: 758e639eebfc83eaf01dddefa0cee0e918f652ace9f9850365d657a3528743c1
authors:
  - people/dev-oyelaran
  - people/mei-tanaka
timestamps:
  created: &id001 '2024-01-14T15:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 0882487a96951b3c7666c2631644bd0f
  status: accepted
relations:
  - predicate: authored_by
    object: people/dev-oyelaran
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/mei-tanaka
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.95
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [121, 153]
        quote: Following up on quarterly close.
---

**From:** Mei Tanaka <mei@meridian.example>

**To:** dev@meridian.example

**Date:** 2024-01-14T15:00:00+00:00

Hi Dev,

Following up on quarterly close. Ana Brito owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Mei Tanaka
