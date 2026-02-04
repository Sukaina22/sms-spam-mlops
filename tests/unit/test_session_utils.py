# tests/unit/test_session_utils.py

import uuid
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)             # .../tests/unit
TESTS_DIR = os.path.dirname(CURRENT_DIR)            # .../tests
ROOT_DIR = os.path.dirname(TESTS_DIR)               # <project_root>

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from ml.utils import ensure_session_id


def test_ensure_session_id_returns_existing_non_empty():
    existing = "my-existing-session-id"
    result = ensure_session_id(existing)

    # Should return the same ID if it's non-empty
    assert result == existing


def test_ensure_session_id_generates_new_when_none():
    result = ensure_session_id(None)

    # Should be a non-empty string
    assert isinstance(result, str)
    assert result != ""

    # And it should be a valid UUID string
    uuid_obj = uuid.UUID(result)  # will raise ValueError if invalid
    assert str(uuid_obj) == result


def test_ensure_session_id_generates_new_when_blank_string():
    result = ensure_session_id("   ")

    # Again, non-empty string
    assert isinstance(result, str)
    assert result.strip() != ""

    # Also must be a valid UUID
    uuid_obj = uuid.UUID(result)
    assert str(uuid_obj) == result
