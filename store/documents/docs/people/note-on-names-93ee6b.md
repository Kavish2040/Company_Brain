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
  model: rules-offline
  prompt_version: roster-v1
  cache_key: f0e66c22bd06a635c316a4e16f58fa62
  status: accepted
relations:
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [69, 94]
        quote: sam.kaur@meridian.example
  - predicate: mentions
    object: people/sam-kelly
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [132, 158]
        quote: sam.kelly@meridian.example
  - predicate: mentions
    object: teams/engineering
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [179, 190]
        quote: Engineering
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [97, 104]
        quote: Finance
  - predicate: mentions
    object: tools/snowflake
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [222, 231]
        quote: Snowflake
---

# Note on names

Two people at Meridian go by "Sam K.":

- Sam Kaur (sam.kaur@meridian.example), Finance Lead, Finance
- Sam Kelly (sam.kelly@meridian.example), Backend Engineer, Engineering

They work together on Project Snowflake, so context alone is often not enough
to tell them apart.
