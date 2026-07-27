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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 2e1775747257f241ac7e4f32a5a8ae93
  status: accepted
relations:
  - predicate: owns
    subject: people/owen-fitz
    object: processes/capacity-planning
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [393, 435]
        quote: 'Capacity planning (owner: Owen Fitzgerald)'
  - predicate: owns
    subject: people/owen-fitz
    object: processes/incident-response
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [270, 312]
        quote: 'Incident response (owner: Owen Fitzgerald)'
  - predicate: owns
    subject: people/priya-raman
    object: processes/release-signoff
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [315, 352]
        quote: 'Release sign-off (owner: Priya Raman)'
  - predicate: owns
    subject: people/tom-whelan
    object: processes/security-review
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [355, 390]
        quote: 'Security review (owner: Tom Whelan)'
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
