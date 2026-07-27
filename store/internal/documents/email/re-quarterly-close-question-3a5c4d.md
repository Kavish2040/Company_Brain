---
id: documents/email/re-quarterly-close-question-3a5c4d
type: Document
title: 'Re: Quarterly close ��� question'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-003.eml
  external_id: email/thread-003.eml
  external_version: 908a5dd9e20d103b
  content_sha256: 908a5dd9e20d103ba5f65374224f0fc9e3524a0cb01935d5c0e26377be16baf6
authors:
  - people/owen-fitz
  - people/priya-raman
timestamps:
  created: &id001 '2024-02-16T14:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: dae832ba44184df326a89c46486e1b19
  status: accepted
relations:
  - predicate: authored_by
    object: people/owen-fitz
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: authored_by
    object: people/priya-raman
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [164, 173]
        quote: Ana Brito
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [27, 48]
        quote: owen@meridian.example
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [59, 81]
        quote: priya@meridian.example
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [147, 162]
        quote: quarterly close
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [201, 209]
        quote: NetSuite
---

**From:** Owen Fitzgerald <owen@meridian.example>

**To:** priya@meridian.example

**Date:** 2024-02-16T14:00:00+00:00

Hi Priya,

Following up on quarterly close. Ana Brito owns this process, but the NetSuite step is blocked on your team.

Can you confirm by Friday?

Thanks,
Owen Fitzgerald
