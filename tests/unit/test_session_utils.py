import uuid
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)             
TESTS_DIR = os.path.dirname(CURRENT_DIR)            
ROOT_DIR = os.path.dirname(TESTS_DIR)               

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from ml.utils import ensure_session_id


def test_ensure_session_id_returns_existing_non_empty():
    existing = "my-existing-session-id"
    result = ensure_session_id(existing)

    assert result == existing


def test_ensure_session_id_generates_new_when_none():
    result = ensure_session_id(None)

    assert isinstance(result, str)
    assert result != ""

    uuid_obj = uuid.UUID(result)
    assert str(uuid_obj) == result


def test_ensure_session_id_generates_new_when_blank_string():
    result = ensure_session_id("   ")

    assert isinstance(result, str)
    assert result.strip() != ""

    uuid_obj = uuid.UUID(result)
    assert str(uuid_obj) == result
