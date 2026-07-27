"""Gmail inbox triage: per-user OAuth + bucketing + web dashboard.

Standalone from the company-brain knowledge-graph pipeline — does not use
Repository, store, ACL, or any of the invariants in CLAUDE.md. Introduces
the first real user-identity (browser session + OAuth token binding).

Refresh is on-demand with 15-minute staleness check: frontend calls
GET /api/gmail/triage every 15 min, backend re-fetches from Gmail only if
cached state is older than that. Single-process in-memory session tracking.
"""
