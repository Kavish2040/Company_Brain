---
id: documents/docs/meetings/release-sign-off-sync-2024-01-18-259749
type: Document
title: Release sign-off sync — 2024-01-18
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-01-18-release-signoff.md
  external_id: docs/meetings/2024-01-18-release-signoff.md
  external_version: fadb8b29e71240e4
  content_sha256: fadb8b29e71240e498ce5b4af77da2b201e0d828a2ce4061fb3a614061e43241
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: b7ae36ac65b16f8e04f517c2745228d1
  status: accepted
relations:
  - predicate: depends_on
    object: tools/zendesk
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [115, 183]
        quote: "Zoë Ravel raised that release sign-off is still blocked on\n Zendesk."
  - predicate: handoff_to
    object: teams/finance
    confidence: 0.5
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [232, 316]
        quote: "Handoff from Engineering to Finance is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: processes/release-signoff
    confidence: 0.8
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [115, 183]
        quote: "Zoë Ravel raised that release sign-off is still blocked on\n Zendesk."
  - predicate: owns
    object: processes/release-signoff
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [186, 229]
        quote: Priya Raman confirmed they own the process.
---

# Release sign-off sync — 2024-01-18

**Attendees:** Zoë Ravel, Sam Kelly, Ana Brito, Owen Fitzgerald

## Notes

- Zoë Ravel raised that release sign-off is still blocked on
 Zendesk.
- Priya Raman confirmed they own the process.
- Handoff from Engineering to Finance is unclear; two
 tickets bounced back last week.

## Actions

- Owen Fitzgerald to document the handoff boundary.
