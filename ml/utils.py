# ml/utils.py
"""
Small, pure helper functions for text preprocessing and probability handling.
These are ideal for unit testing because they have no side effects.
"""

import re
import uuid


def clean_text(text: str) -> str:
    """
    Normalize SMS text:
    - strip leading/trailing whitespace
    - convert to lowercase
    - collapse multiple spaces/newlines into a single space
    """
    # strip and lowercase
    text = text.strip().lower()
    # collapse any runs of whitespace (spaces, tabs, newlines) into a single space
    text = re.sub(r"\s+", " ", text)
    return text


def prob_to_label(spam_prob: float, threshold: float = 0.5) -> str:
    """
    Convert a spam probability into a label.

    Args:
        spam_prob: model probability that the message is spam (0–1).
        threshold: decision threshold. Default 0.5.

    Returns:
        "spam" if spam_prob >= threshold, else "ham".
    """
    return "spam" if spam_prob >= threshold else "ham"


def clamp_probability(p: float) -> float:
    """
    Ensure a probability is in [0.0, 1.0].

    - Values below 0 become 0.0
    - Values above 1 become 1.0
    - Values in between are returned unchanged
    """
    if p < 0.0:
        return 0.0
    if p > 1.0:
        return 1.0
    return p

def ensure_session_id(session_id: str | None) -> str:
    """
    Return a valid session ID string.

    - If a non-empty session_id is provided, return it unchanged.
    - If None or only whitespace is provided, generate a new UUID4 string.
    """
    if session_id is not None and session_id.strip():
        return session_id
    return str(uuid.uuid4())
