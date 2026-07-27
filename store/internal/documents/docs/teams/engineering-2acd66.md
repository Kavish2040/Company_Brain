---
id: documents/docs/teams/engineering-2acd66
type: Document
title: Engineering
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/teams/engineering.md
  external_id: docs/teams/engineering.md
  external_version: a1fe7b8b18911c72
  content_sha256: a1fe7b8b18911c72a88962510656c4907b68671238f13191b2b084ce0fb971d1
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 6dbc958e43cd38026debc79cf3bf3a7a
  status: accepted
relations:
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [224, 245]
        quote: owen@meridian.example
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [119, 141]
        quote: priya@meridian.example
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [59, 85]
        quote: sam.kelly@meridian.example
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [177, 197]
        quote: tom@meridian.example
  - predicate: mentions
    object: processes/capacity-planning
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [393, 410]
        quote: Capacity planning
  - predicate: mentions
    object: processes/incident-response
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [270, 287]
        quote: Incident response
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [315, 331]
        quote: Release sign-off
  - predicate: mentions
    object: processes/security-review
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [355, 370]
        quote: Security review
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 13]
        quote: Engineering
---

# Engineering

## Members

- Sam Kelly — Backend Engineer (sam.kelly@meridian.example)
- Priya Raman — VP Engineering (priya@meridian.example)
- Tom Whelan — Platform Engineer (tom@meridian.example)
- Owen Fitzgerald — SRE (owen@meridian.example)

## Processes owned

- Incident response (owner: Owen Fitzgerald)
- Release sign-off (owner: Priya Raman)
- Security review (owner: Tom Whelan)
- Capacity planning (owner: Owen Fitzgerald)
