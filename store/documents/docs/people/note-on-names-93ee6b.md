---
id: documents/docs/people/note-on-names-93ee6b
type: Document
title: Note on names
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/people/disambiguation.md
  external_id: docs/people/disambiguation.md
  external_version: 8492da36c42242ab
  content_sha256: 8492da36c42242ab7bdcec072bed46242d3689597bc0b0084549cc9e06f3ac64
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 831fc2b559bc1c56cf5b9f914431fb91
  status: accepted
relations:
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.95
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [59, 118]
        quote: Sam Kaur (sam.kaur@meridian.example), Finance Lead, Finance
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.95
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [121, 190]
        quote: Sam Kelly (sam.kelly@meridian.example), Backend Engineer, Engineering
  - predicate: mentions
    object: teams/engineering
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [121, 190]
        quote: Sam Kelly (sam.kelly@meridian.example), Backend Engineer, Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.7
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [59, 118]
        quote: Sam Kaur (sam.kaur@meridian.example), Finance Lead, Finance
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.4
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [192, 289]
        quote: 'They work together on Project Snowflake, so context alone is often not enough

          to tell them apart.'
---

# Note on names

Two people at Meridian go by "Sam K.":

- Sam Kaur (sam.kaur@meridian.example), Finance Lead, Finance
- Sam Kelly (sam.kelly@meridian.example), Backend Engineer, Engineering

They work together on Project Snowflake, so context alone is often not enough
to tell them apart.
