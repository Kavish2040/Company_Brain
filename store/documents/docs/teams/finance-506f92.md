---
id: documents/docs/teams/finance-506f92
type: Document
title: Finance
status: active
acl:
  ref: fs:corpus:docs
  sensitivity: internal
source:
  connector: local_fs
  uri: file://corpus/docs/teams/finance.md
  external_id: docs/teams/finance.md
  external_version: 75c9942681b8177e
  content_sha256: 75c9942681b8177e12205394c8598e80a22434f10408486fa48f11ab144627ce
normalizer:
  name: markdown
  version: 1.0.0
extraction:
  model: rules-offline
  prompt_version: roster-v1
  cache_key: 3fb7bf815176d96bef5eec85766528fd
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [103, 123]
        quote: ana@meridian.example
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [50, 75]
        quote: sam.kaur@meridian.example
  - predicate: mentions
    object: processes/quarterly-close
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [183, 198]
        quote: Quarterly close
  - predicate: mentions
    object: processes/refund-approval
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [220, 235]
        quote: Refund approval
  - predicate: mentions
    object: processes/vendor-renewal
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [148, 162]
        quote: Vendor renewal
  - predicate: mentions
    object: teams/finance
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [2, 9]
        quote: Finance
---

# Finance

## Members

- Sam Kaur — Finance Lead (sam.kaur@meridian.example)
- Ana Brito — Controller (ana@meridian.example)

## Processes owned

- Vendor renewal (owner: Sam Kaur)
- Quarterly close (owner: Ana Brito)
- Refund approval (owner: Ana Brito)
