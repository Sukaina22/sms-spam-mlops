# tests/integration/test_api_integration.py

import os
import sys
from uuid import uuid4

from fastapi.testclient import TestClient

# -------------------------------------------------------------------------
# 1. Make sure Python can import from the project root
# -------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(__file__)         # .../tests/integration
TESTS_DIR = os.path.dirname(CURRENT_DIR)        # .../tests
ROOT_DIR = os.path.dirname(TESTS_DIR)           # project root (SMS_Spam_MLOps)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# -------------------------------------------------------------------------
# 2. Use a SEPARATE DB for tests
#    This avoids touching your real sms_history.db
# -------------------------------------------------------------------------
TEST_DB_PATH = os.path.join(ROOT_DIR, "test_sms_history.db")
os.environ["DB_PATH"] = TEST_DB_PATH  # <- main.py reads this as DB_PATH

# Now we can safely import the FastAPI app and init_db from app.main
from app.main import app, init_db   # noqa: E402

# FastAPI TestClient – no need to run uvicorn
client = TestClient(app)


# -------------------------------------------------------------------------
# 3. Global setup for this module
#    Runs ONCE before all tests in this file
# -------------------------------------------------------------------------
def setup_module(module):
    """
    Ensure a clean test DB with the 'predictions' table created.
    """
    # Remove old test DB if it exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # Recreate DB + 'predictions' table for tests
    init_db()
# -------------------------------------------------------------------------


def test_predict_returns_label_and_probability():
    session_id = str(uuid4())
    payload = {
        "text": "FREE FREE FREE! You have won a $1000 gift card.",
        "session_id": session_id,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200

    data = response.json()

    # Your real API returns 'label', 'confidence', 'session_id'
    assert "label" in data
    assert "confidence" in data
    assert "session_id" in data

    assert data["label"] in ("spam", "ham")
    assert 0.0 <= float(data["confidence"]) <= 1.0



def test_predict_creates_history_entry():
    session_id = str(uuid4())
    sms_text = "Hey, I'll be late today. Let's meet around 7pm instead."

    # Call /predict
    resp_predict = client.post(
        "/predict",
        json={"text": sms_text, "session_id": session_id},
    )
    assert resp_predict.status_code == 200

    # Then call /history/{session_id}
    resp_history = client.get(f"/history/{session_id}")
    assert resp_history.status_code == 200

    history = resp_history.json()
    assert isinstance(history, list)
    assert len(history) >= 1

    # By your design, each item in history should have sms_text/label/confidence
    assert any(item["sms_text"] == sms_text for item in history)


def test_history_is_isolated_per_session():
    session_a = str(uuid4())
    session_b = str(uuid4())

    sms_a = "Message for session A only."
    sms_b = "Message for session B only."

    # Predict for session A
    resp_a = client.post(
        "/predict",
        json={"text": sms_a, "session_id": session_a},
    )
    assert resp_a.status_code == 200

    # Predict for session B
    resp_b = client.post(
        "/predict",
        json={"text": sms_b, "session_id": session_b},
    )
    assert resp_b.status_code == 200

    # Get history for A
    history_a = client.get(f"/history/{session_a}").json()
    # Get history for B
    history_b = client.get(f"/history/{session_b}").json()

    # A's history contains A's message but not B's
    assert any(item["sms_text"] == sms_a for item in history_a)
    assert all(item["sms_text"] != sms_b for item in history_a)

    # B's history contains B's message but not A's
    assert any(item["sms_text"] == sms_b for item in history_b)
    assert all(item["sms_text"] != sms_a for item in history_b)
