---
id: documents/slack/support/slack-thread-2024-01-13-2a7b7d
type: Document
title: Slack thread — 2024-01-13
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-13.json
  external_id: slack/support/2024-01-13.json
  external_version: 66426117f9661d67
  content_sha256: 66426117f9661d671adcbf63b12de9c531d27da8bede9c16ab6dfe76232daeec
timestamps:
  created: '2024-01-13T11:30:00Z'
  modified: '2024-01-13T11:44:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: f7936ccbe0761ff8a2ee228b787b6a1f
  status: accepted
relations:
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [109, 119]
        quote: Mei Tanaka
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 17]
        quote: Owen Fitzgerald
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [190, 207]
        quote: Capacity planning
  - predicate: mentions
    object: processes/onboarding
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [293, 312]
        quote: Employee onboarding
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [88, 104]
        quote: Release sign-off
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [73, 84]
        quote: Engineering
---

**Owen Fitzgerald** (11:30): This is the fourth ticket bounced back from Engineering on Release sign-off.

**Mei Tanaka** (11:37): This is the fourth ticket bounced back from Engineering on Capacity planning.

**Mei Tanaka** (11:44): This is the fourth ticket bounced back from Engineering on Employee onboarding.
