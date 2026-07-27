"""Email classification into buckets based on Gmail's own labels.

Rule-based only — no LLM. Deterministic, matches Gmail's own tab taxonomy.
"""

from enum import StrEnum


class EmailBucket(StrEnum):
    """The five buckets for email classification."""

    URGENT = "urgent"
    PROMOTIONAL = "promotional"
    SOCIAL = "social"
    UPDATES = "updates"
    NORMAL = "normal"


def classify_message(labels: list[str], starred: bool = False) -> EmailBucket:
    """Classify a message into a bucket based on its labels and star status.

    Priority order:
    1. IMPORTANT label or starred → urgent
    2. CATEGORY_PROMOTIONS → promotional
    3. CATEGORY_SOCIAL → social
    4. CATEGORY_UPDATES or CATEGORY_FORUMS → updates
    5. else → normal
    """
    label_set = set(labels)

    if "IMPORTANT" in label_set or starred:
        return EmailBucket.URGENT

    if "CATEGORY_PROMOTIONS" in label_set:
        return EmailBucket.PROMOTIONAL

    if "CATEGORY_SOCIAL" in label_set:
        return EmailBucket.SOCIAL

    if "CATEGORY_UPDATES" in label_set or "CATEGORY_FORUMS" in label_set:
        return EmailBucket.UPDATES

    return EmailBucket.NORMAL
