---
id: documents/email/re-refund-approval-approval-needed-dae3d7
type: Document
title: 'Re: Refund approval ��� approval needed'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-015.eml
  external_id: email/thread-015.eml
  external_version: bb83cfc9ce3e3d4e
  content_sha256: bb83cfc9ce3e3d4e119cba93d5c756f0ea765051f86f0b196c9fe14cf8234782
authors:
  - people/sam-kaur
  - people/sam-kelly
timestamps:
  created: &id001 '2024-02-17T15:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: fd2aee1b72250052e7ac9b8d37217cd4
  status: accepted
relations:
  - predicate: authored_by
    object: people/sam-kaur
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/sam-kelly
    confidence: 1.0
    provenance: structural
    status: accepted
---

**From:** Sam Kaur <sam.kaur@meridian.example>

**To:** sam.kelly@meridian.example

**Date:** 2024-02-17T15:00:00+00:00

Hi Sam,

Following up on refund approval. Ana Brito owns this process, but the Zendesk step is blocked on your team.

Can you confirm by Friday?

Thanks,
Sam Kaur
