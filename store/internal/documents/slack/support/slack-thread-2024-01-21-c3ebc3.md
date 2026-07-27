---
id: documents/slack/support/slack-thread-2024-01-21-c3ebc3
type: Document
title: Slack thread — 2024-01-21
status: active
acl:
  ref: slack:channel:C0SUP
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/slack/support/2024-01-21.json
  external_id: slack/support/2024-01-21.json
  external_version: 307bd95e1ce50ded
  content_sha256: 307bd95e1ce50ded853f9a67ed2702a1b1ac73ee399eca8cb243964201232808
timestamps:
  created: '2024-01-21T13:04:00Z'
  modified: '2024-01-21T13:25:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: ef8bd0dd80aba01b61235b1c97b4ba1d
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [299, 308]
        quote: Ana Brito
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [195, 207]
        quote: Nadia Hassan
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
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [110, 119]
        quote: Sam Kelly
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [88, 105]
        quote: Capacity planning
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [379, 396]
        quote: Incident response
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [160, 175]
        quote: Quarterly close
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [73, 84]
        quote: Engineering
  - predicate: mentions
    object: tools/zendesk
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [259, 266]
        quote: Zendesk
---

**Owen Fitzgerald** (13:04): This is the fourth ticket bounced back from Engineering on Capacity planning.

**Sam Kelly** (13:11): Customer is asking about the Quarterly close timeline again.

**Nadia Hassan** (13:18): Escalating this to Engineering — it's a Zendesk integration bug, not config.

**Ana Brito** (13:25): This is the fourth ticket bounced back from Engineering on Incident response.
