---
id: documents/email/re-refund-approval-approval-needed-069023
type: Document
title: 'Re: Refund approval ��� approval needed'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-014.eml
  external_id: email/thread-014.eml
  external_version: dfb266bcfa3a99d2
  content_sha256: dfb266bcfa3a99d261949fc98054d9686ad86f4b355756368b44b9d257b4382d
authors:
  - people/sam-kelly
  - people/tom-whelan
timestamps:
  created: &id001 '2024-02-23T16:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 4f6bb1698f01e771063579bbc1077d84
  status: accepted
relations:
  - predicate: authored_by
    object: people/sam-kelly
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/tom-whelan
    confidence: 1.0
    provenance: structural
    status: accepted
---

**From:** Tom Whelan <tom@meridian.example>

**To:** sam.kelly@meridian.example

**Date:** 2024-02-23T16:00:00+00:00

Hi Sam,

Following up on refund approval. Ana Brito owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Tom Whelan
