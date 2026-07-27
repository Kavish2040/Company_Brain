---
id: documents/email/re-release-sign-off-status-c9f4fe
type: Document
title: 'Re: Release sign-off ��� status'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-004.eml
  external_id: email/thread-004.eml
  external_version: 21f0d098430eb5b7
  content_sha256: 21f0d098430eb5b7b63f86211b50232d7d0463a105b6658f3e71c858e0fb5869
authors:
  - people/nadia-hassan
timestamps:
  created: &id001 '2024-03-05T11:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 0a99423569bf89aa3108dbb1b14825ae
  status: accepted
relations:
  - predicate: authored_by
    object: people/nadia-hassan
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: depends_on
    subject: processes/release-signoff
    object: tools/linear
    confidence: 0.65
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [163, 238]
        quote: Priya Raman owns this process, but the Linear step is blocked on your team.
  - predicate: owns
    subject: people/priya-raman
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [163, 238]
        quote: Priya Raman owns this process, but the Linear step is blocked on your team.
---

**From:** Nadia Hassan <nadia@meridian.example>

**To:** nadia@meridian.example

**Date:** 2024-03-05T11:00:00+00:00

Hi Nadia,

Following up on release sign-off. Priya Raman owns this process, but the Linear step is blocked on your team.

Can you confirm by Friday?

Thanks,
Nadia Hassan
