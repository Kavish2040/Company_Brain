---
id: documents/docs/meetings/capacity-planning-sync-2024-01-24-4b153e
type: Document
title: Capacity planning sync — 2024-01-24
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-24-capacity-planning.md
  external_id: docs/meetings/2024-01-24-capacity-planning.md
  external_version: c8df2649e397c352
  content_sha256: c8df2649e397c352dec4ffecc982cac1e16ad4101cff4505632d8a009a60e69e
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: d354829934b99edf77d69d68737581cc
  status: accepted
relations:
  - predicate: depends_on
    object: tools/pagerduty
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [113, 184]
        quote: "Sam Kelly raised that capacity planning is still blocked on\n PagerDuty."
  - predicate: handoff_to
    object: teams/engineering
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [237, 321]
        quote: "Handoff from Finance to Engineering is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [337, 383]
        quote: Nadia Hassan to document the handoff boundary.
  - predicate: owns
    object: processes/capacity-planning
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [187, 234]
        quote: Owen Fitzgerald confirmed they own the process.
---

# Capacity planning sync — 2024-01-24

**Attendees:** Sam Kelly, Sam Kaur, Tom Whelan, Nadia Hassan

## Notes

- Sam Kelly raised that capacity planning is still blocked on
 PagerDuty.
- Owen Fitzgerald confirmed they own the process.
- Handoff from Finance to Engineering is unclear; two
 tickets bounced back last week.

## Actions

- Nadia Hassan to document the handoff boundary.
