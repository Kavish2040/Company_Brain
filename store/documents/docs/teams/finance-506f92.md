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
  model: claude-sonnet-5
  prompt_version: claude-roster-v2
  cache_key: 80af3d5f0fa3086057d67f64f3e9a234
  status: accepted
relations:
  - predicate: mentions
    object: people/ana-brito
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [79, 124]
        quote: Ana Brito — Controller (ana@meridian.example)
  - predicate: mentions
    object: people/sam-kaur
    confidence: 0.9
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [25, 76]
        quote: Sam Kaur — Finance Lead (sam.kaur@meridian.example)
  - predicate: mentions
    object: teams/finance
    confidence: 0.85
    provenance: llm
    status: accepted
    evidence:
      - node: self
        span: [0, 9]
        quote: '# Finance'
  - predicate: owns
    subject: people/ana-brito
    object: processes/quarterly-close
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [183, 217]
        quote: 'Quarterly close (owner: Ana Brito)'
  - predicate: owns
    subject: people/ana-brito
    object: processes/refund-approval
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [220, 254]
        quote: 'Refund approval (owner: Ana Brito)'
  - predicate: owns
    subject: people/sam-kaur
    object: processes/vendor-renewal
    confidence: 0.98
    provenance: llm
    status: proposed
    evidence:
      - node: self
        span: [148, 180]
        quote: 'Vendor renewal (owner: Sam Kaur)'
---

# Finance

## Members

- Sam Kaur — Finance Lead (sam.kaur@meridian.example)
- Ana Brito — Controller (ana@meridian.example)

## Processes owned

- Vendor renewal (owner: Sam Kaur)
- Quarterly close (owner: Ana Brito)
- Refund approval (owner: Ana Brito)
