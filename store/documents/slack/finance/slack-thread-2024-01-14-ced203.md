---
id: documents/slack/finance/slack-thread-2024-01-14-ced203
type: Document
title: Slack thread — 2024-01-14
status: active
acl:
  ref: slack:channel:C0FIN
  sensitivity: restricted
source:
  connector: local_fs
  uri: file://corpus/slack/finance/2024-01-14.json
  external_id: slack/finance/2024-01-14.json
  external_version: a94689329ea31ec7
  content_sha256: a94689329ea31ec73d113fd65973ab0023597361048358beac198f4ca8d9b1eb
timestamps:
  created: '2024-01-14T13:12:00Z'
  modified: '2024-01-14T13:26:00Z'
normalizer:
  name: slack_export
  version: 1.0.0
extraction:
  model: claude-sonnet-5
  prompt_version: claude-roster-v1
  cache_key: c79cfd79a6a57d07757b8bac126154b8
  status: accepted
---

**Sam Kaur** (13:12): The Snowflake renewal lands in April. I own that end to end.

**Ana Brito** (13:19): Quarterly close is blocked until Engineering signs off on the security review.

**Sam Kaur** (13:26): Customer data request is blocked until Engineering signs off on the security review.
