import re
import uuid

def clean_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def prob_to_label(spam_prob: float, threshold: float = 0.5) -> str:
    return "spam" if spam_prob >= threshold else "ham"


def clamp_probability(p: float) -> float:
    if p < 0.0:
        return 0.0
    if p > 1.0:
        return 1.0
    return p

def ensure_session_id(session_id: str | None) -> str:
    if session_id is not None and session_id.strip():
        return session_id
    return str(uuid.uuid4())
