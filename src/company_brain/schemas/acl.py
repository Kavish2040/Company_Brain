"""Access control.

A node carries a *reference* to its source system's ACL object, never a copy of
that object's membership (docs/ARCHITECTURE.md §6.1). Someone leaving a Slack
channel is then one row in ``acl_grants``, not a rewrite of every markdown file
that channel ever produced.

Sensitivity is coarse and separate: it selects the physical store root and the
vector-index partition, so it must be decidable without consulting the grants
table.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from enum import StrEnum
from typing import Final

from pydantic import BaseModel, ConfigDict, field_validator


class Sensitivity(StrEnum):
    """Coarse tier. Ordered least- to most-restrictive; see `at_least`."""

    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"


_TIER_ORDER: Final[dict[Sensitivity, int]] = {
    Sensitivity.PUBLIC: 0,
    Sensitivity.INTERNAL: 1,
    Sensitivity.RESTRICTED: 2,
}


def narrowest(tiers: Iterable[Sensitivity]) -> Sensitivity:
    """Most restrictive tier in an iterable. Empty input is RESTRICTED.

    Fail-closed on empty is deliberate: a derived node with no discoverable
    inputs must not default to visible (invariant 6).
    """
    materialised = list(tiers)
    if not materialised:
        return Sensitivity.RESTRICTED
    return max(materialised, key=lambda t: _TIER_ORDER[t])


# e.g. "slack:channel:C0ENG", "gdrive:file:1a2b3c", "fs:corpus:public"
_ACL_REF = re.compile(r"^[a-z0-9_]+:[a-z0-9_]+:[A-Za-z0-9_.\-]+$")


class AclRef(BaseModel):
    """Opaque pointer to a source system's permission object."""

    model_config = ConfigDict(frozen=True)

    ref: str
    sensitivity: Sensitivity

    @field_validator("ref")
    @classmethod
    def _well_formed(cls, v: str) -> str:
        if not _ACL_REF.match(v):
            raise ValueError(f"acl ref must be '<connector>:<kind>:<external_id>', got {v!r}")
        return v

    @property
    def connector(self) -> str:
        return self.ref.split(":", 1)[0]


class PrincipalKind(StrEnum):
    USER = "user"
    GROUP = "group"
    AGENT = "agent"
    SERVICE = "service"


class Principal(BaseModel):
    """The requesting identity. Every read path takes one explicitly (invariant 5).

    ``delegated_by`` is set when an agent acts for a human; the effective visible
    set is then the intersection of both parties' grants (invariant 8), computed
    in the acl package rather than here.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    kind: PrincipalKind
    display: str
    delegated_by: str | None = None

    @field_validator("delegated_by")
    @classmethod
    def _no_self_delegation(cls, v: str | None, info: object) -> str | None:
        # A principal delegating to itself would quietly widen nothing, but it
        # signals a bug in session setup — reject it rather than absorb it.
        data = getattr(info, "data", {})
        if v is not None and v == data.get("id"):
            raise ValueError("principal cannot delegate to itself")
        return v
