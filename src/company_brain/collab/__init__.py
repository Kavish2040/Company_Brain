"""Demo-grade live collaboration.

Server-authoritative, last-write-wins, no CRDT. See docs/ARCHITECTURE.md §15 for
what that costs and `session.py` for where it loses data.
"""

from company_brain.collab.guard import FenceViolation, check_generated_regions
from company_brain.collab.hub import CollabHub
from company_brain.collab.session import (
    PALETTE,
    EditOutcome,
    Participant,
    RoomState,
    SessionRegistry,
    participant_color,
)

__all__ = [
    "PALETTE",
    "CollabHub",
    "EditOutcome",
    "FenceViolation",
    "Participant",
    "RoomState",
    "SessionRegistry",
    "check_generated_regions",
    "participant_color",
]
