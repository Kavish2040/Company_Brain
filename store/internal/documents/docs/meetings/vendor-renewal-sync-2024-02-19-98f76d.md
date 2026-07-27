---
id: documents/docs/meetings/vendor-renewal-sync-2024-02-19-98f76d
type: Document
title: Vendor renewal sync — 2024-02-19
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/meetings/2024-02-19-vendor-renewal.md
  external_id: docs/meetings/2024-02-19-vendor-renewal.md
  external_version: 71bf05bdc854385b
  content_sha256: 71bf05bdc854385b97f449a9ce89ba32f06255d24fab92438a9722c3bc2c8b07
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 4fb6b0dd674a6893c2485c75249b82e9
  status: accepted
relations:
  - predicate: depends_on
    subject: processes/vendor-renewal
    object: tools/pagerduty
    confidence: 0.85
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [117, 188]
        quote: "Nadia Hassan raised that vendor renewal is still blocked on\n PagerDuty."
  - predicate: handoff_to
    subject: teams/product
    object: teams/support
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [234, 314]
        quote: "Handoff from Product to Support is unclear; two\n tickets bounced back last week."
  - predicate: mentions
    object: people/mei-tanaka
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [51, 103]
        quote: Nadia Hassan, Zoë Ravel, Mei Tanaka, Owen Fitzgerald
  - predicate: mentions
    object: people/nadia-hassan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [51, 103]
        quote: Nadia Hassan, Zoë Ravel, Mei Tanaka, Owen Fitzgerald
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [51, 103]
        quote: Nadia Hassan, Zoë Ravel, Mei Tanaka, Owen Fitzgerald
  - predicate: mentions
    object: people/zoe-ravel
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [51, 103]
        quote: Nadia Hassan, Zoë Ravel, Mei Tanaka, Owen Fitzgerald
  - predicate: owns
    subject: people/sam-kaur
    object: processes/vendor-renewal
    confidence: 0.75
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [191, 231]
        quote: Sam Kaur confirmed they own the process.
---

# Vendor renewal sync — 2024-02-19

**Attendees:** Nadia Hassan, Zoë Ravel, Mei Tanaka, Owen Fitzgerald

## Notes

- Nadia Hassan raised that vendor renewal is still blocked on
 PagerDuty.
- Sam Kaur confirmed they own the process.
- Handoff from Product to Support is unclear; two
 tickets bounced back last week.

## Actions

- Owen Fitzgerald to document the handoff boundary.
