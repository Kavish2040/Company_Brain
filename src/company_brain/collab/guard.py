"""Server-side validation of a live edit.

Invariant 13 says machine writers touch only the interior of a generated fence,
and never human text. Live editing is the mirror image: a *human* writer may
touch only the text outside every fence, and never a generated interior.

The check lives here — on the server — because a browser is not a trust
boundary. A client that strips a fence, renames a region, or rewrites a
generated interior gets rejected and resynced rather than persisted.
"""

from __future__ import annotations

from company_brain.store.fences import FenceError, Region, find_regions


class FenceViolation(ValueError):
    """A live edit changed generated content, not just human content."""


def _describe(regions: list[Region]) -> str:
    return ", ".join(r.name for r in regions) or "none"


def check_generated_regions(stored: str, submitted: str) -> None:
    """Raise unless every generated region survived the edit untouched.

    Compares name, interior, and recorded hash region-by-region in document
    order. Position is deliberately *not* compared: a human adding a paragraph
    above a fence shifts its offsets, and that is exactly the edit we want to
    allow.
    """
    try:
        before = find_regions(stored)
        after = find_regions(submitted)
    except FenceError as exc:
        # Malformed fences on either side are indistinguishable from tampering
        # at this layer, and both are unsafe to persist.
        raise FenceViolation(str(exc)) from exc

    if len(before) != len(after):
        raise FenceViolation(
            f"generated regions were added or removed: "
            f"had [{_describe(before)}], got [{_describe(after)}]"
        )

    for original, edited in zip(before, after, strict=True):
        if original.name != edited.name:
            raise FenceViolation(
                f"generated regions were reordered or renamed: "
                f"expected {original.name!r}, got {edited.name!r}"
            )
        if original.recorded_hash != edited.recorded_hash:
            raise FenceViolation(f"the recorded hash of region {original.name!r} was rewritten")
        if original.content != edited.content:
            raise FenceViolation(
                f"the interior of generated region {original.name!r} was edited"
            )
