---
id: documents/email/re-employee-onboarding-approval-needed-58de84
type: Document
title: 'Re: Employee onboarding ��� approval needed'
status: active
acl:
  ref: gmail:mailbox:meridian
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/email/thread-016.eml
  external_id: email/thread-016.eml
  external_version: 1d99edd4383ef417
  content_sha256: 1d99edd4383ef4179ec817af8a2fb83d5616af84511382f23fb4607eb56aef7f
authors:
  - people/tom-whelan
timestamps:
  created: &id001 '2024-01-16T11:00:00Z'
  modified: *id001
normalizer:
  name: email
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 3ac96e6d80d7f3ac302f98bb2c321c53
  status: accepted
relations:
  - predicate: authored_by
    object: people/tom-whelan
    confidence: 1.0
    provenance: structural
    status: accepted
  - predicate: depends_on
    object: tools/snowflake
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [158, 234]
        quote: Zoë Ravel owns this process, but the Snowflake step is blocked on your team.
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [121, 157]
        quote: Following up on employee onboarding.
  - predicate: owns
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [158, 234]
        quote: Zoë Ravel owns this process, but the Snowflake step is blocked on your team.
---

**From:** Tom Whelan <tom@meridian.example>

**To:** tom@meridian.example

**Date:** 2024-01-16T11:00:00+00:00

Hi Tom,

Following up on employee onboarding. Zoë Ravel owns this process, but the Snowflake step is blocked on your team.

Can you confirm by Friday?

Thanks,
Tom Whelan
