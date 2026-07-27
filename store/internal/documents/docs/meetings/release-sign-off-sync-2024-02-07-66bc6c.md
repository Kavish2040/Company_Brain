---
id: documents/docs/meetings/release-sign-off-sync-2024-02-07-66bc6c
type: Document
title: Release sign-off sync — 2024-02-07
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-07-release-signoff.md
  external_id: docs/meetings/2024-02-07-release-signoff.md
  external_version: 9bac790efce9f58f
  content_sha256: 9bac790efce9f58f45b39de1f1c7d26790308939729da2fabf67534f37392991
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 080ec2b25429e458f590a511c7070c18
  status: accepted
relations:
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [186, 229]
        quote: Priya Raman confirmed they own the process.
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [332, 375]
        quote: Sam Kelly to document the handoff boundary.
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [114, 183]
        quote: "Mei Tanaka raised that release sign-off is still blocked on\n Datadog."
  - predicate: mentions
    object: tools/datadog
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [114, 183]
        quote: "Mei Tanaka raised that release sign-off is still blocked on\n Datadog."
  - predicate: owns
    subject: people/priya-raman
    object: processes/release-signoff
    confidence: 0.6
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [186, 229]
        quote: Priya Raman confirmed they own the process.
---

# Release sign-off sync — 2024-02-07

**Attendees:** Mei Tanaka, Tom Whelan, Dev Oyelaran, Sam Kelly

## Notes

- Mei Tanaka raised that release sign-off is still blocked on
 Datadog.
- Priya Raman confirmed they own the process.
- Handoff from Engineering to Support is unclear; two
 tickets bounced back last week.

## Actions

- Sam Kelly to document the handoff boundary.
