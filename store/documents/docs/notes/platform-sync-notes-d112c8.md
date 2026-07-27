---
id: documents/docs/notes/platform-sync-notes-d112c8
type: Document
title: Platform sync notes
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/notes/platform-sync-notes.md
  external_id: docs/notes/platform-sync-notes.md
  external_version: 20489ab3adf1a8cc
  content_sha256: 20489ab3adf1a8ccc8146a3d040f8dc1d5f4db14db3e6f04f36cf20d5bb1a108
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: 6c0d24cba23e59d4a316531eb4ce76fe
  status: accepted
relations:
  - predicate: mentions
    object: people/owen-fitz
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 69]
        quote: 'Attendees: Sam K., Tom Whelan, Owen Fitzgerald'
  - predicate: mentions
    object: people/tom-whelan
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [23, 69]
        quote: 'Attendees: Sam K., Tom Whelan, Owen Fitzgerald'
---

# Platform sync notes

Attendees: Sam K., Tom Whelan, Owen Fitzgerald

Sam K. is migrating the ingest workers off the legacy queue. Sam flagged that
Project Snowflake will need a schema freeze first.

Action: Sam K. to write the migration RFC.
