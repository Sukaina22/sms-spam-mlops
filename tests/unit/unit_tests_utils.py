# tests/unit/test_utils.py

import pytest

from ml.utils import clean_text, prob_to_label, clamp_probability


def test_clean_text_normalizes_whitespace_and_lowercase():
    raw = "   Hello   WORLD \n\n this   IS   SPAM  "
    cleaned = clean_text(raw)

    # Should be lowercase
    assert cleaned == "hello world this is spam"

    # No leading/trailing spaces
    assert cleaned == cleaned.strip()

    # No double spaces inside
    assert "  " not in cleaned


def test_prob_to_label_uses_threshold_correctly():
    # Below threshold -> ham
    assert prob_to_label(0.3, threshold=0.5) == "ham"

    # Equal to threshold -> spam
    assert prob_to_label(0.5, threshold=0.5) == "spam"

    # Above threshold -> spam
    assert prob_to_label(0.9, threshold=0.5) == "spam"


def test_clamp_probability_keeps_values_in_range():
    # Below 0 -> 0.0
    assert clamp_probability(-0.3) == pytest.approx(0.0)

    # Between 0 and 1 -> unchanged
    assert clamp_probability(0.42) == pytest.approx(0.42)

    # Above 1 -> 1.0
    assert clamp_probability(1.7) == pytest.approx(1.0)
