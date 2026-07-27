---
id: documents/docs/notes/vendor-sync-notes-2692d3
type: Document
title: Vendor sync notes
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/notes/vendor-sync-notes.md
  external_id: docs/notes/vendor-sync-notes.md
  external_version: 0260333fb4114483
  content_sha256: 0260333fb411448307562c38129fddbc30d90a9807214b3b3484cb5f66b01c38
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v2
  cache_key: 5e430cdf0e524bce365cbdc0ebc39ddb
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [53, 62]
        quote: Ana Brito
  - predicate: mentions
    object: people/priya-raman
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [40, 51]
        quote: Priya Raman
  - predicate: mentions
    object: tools/netsuite
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [85, 93]
        quote: NetSuite
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [152, 161]
        quote: Snowflake
---

# Vendor sync notes

Attendees: Sam K., Priya Raman, Ana Brito

Sam K. confirmed the NetSuite renewal is on track for April. Sam is also
picking up the Snowflake contract review.

Action: Sam K. to circulate the renewal calendar.
