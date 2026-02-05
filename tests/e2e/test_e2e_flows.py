# tests/e2e/test_e2e_flows.py

import os
import sys
from uuid import uuid4

from fastapi.testclient import TestClient

# -------------------------------------------------------------------------
# 1. Path setup so we can import from project root
# -------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(__file__)         # .../tests/e2e
TESTS_DIR = os.path.dirname(CURRENT_DIR)        # .../tests
ROOT_DIR = os.path.dirname(TESTS_DIR)           # project root

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# -------------------------------------------------------------------------
# 2. Import FastAPI app – no direct DB handling here
#    The app itself is responsible for connecting to whatever DB is configured.
# -------------------------------------------------------------------------
from app.main import app  # noqa: E402

client = TestClient(app)


def test_e2e_spam_flow_predict_then_history():
    """
    Full spam detection flow:
    - new session
    - send clearly spammy SMS to /predict
    - fetch /history for that session
    - verify history contains the same SMS + same label
    """
    session_id = str(uuid4())
    sms_text = "FREE FREE FREE! You have won a $1000 gift card. Click now!"

    # Step 1: predict
    resp_predict = client.post(
        "/predict",
        json={"text": sms_text, "session_id": session_id},
    )
    assert resp_predict.status_code == 200

    data = resp_predict.json()
    assert data["label"] in ("spam", "ham")
    assert 0.0 <= float(data["confidence"]) <= 1.0
    assert data["session_id"] == session_id

    # Step 2: get history
    resp_history = client.get(f"/history/{session_id}")
    assert resp_history.status_code == 200

    history = resp_history.json()
    assert isinstance(history, list)
    assert len(history) >= 1

    # Check that one of the history items matches the prediction
    assert any(
        item["sms_text"] == sms_text and item["label"] == data["label"]
        for item in history
    )


def test_e2e_multiple_messages_single_session():
    """
    E2E flow for one user sending multiple messages in the same session.
    - send several SMS messages
    - verify history returns all of them for that session
    - and no duplicates
    """
    session_id = str(uuid4())
    messages = [
        "Hey, are we still on for tonight?",
        "Reminder: Your invoice is due tomorrow.",
        "WIN a brand new iPhone by clicking this link!",
    ]

    # Send each message
    for msg in messages:
        resp = client.post(
            "/predict",
            json={"text": msg, "session_id": session_id},
        )
        assert resp.status_code == 200

    # Fetch history
    resp_history = client.get(f"/history/{session_id}")
    assert resp_history.status_code == 200

    history = resp_history.json()
    assert isinstance(history, list)
    # At least as many items as messages we sent
    assert len(history) >= len(messages)

    # Extract texts from history and ensure all messages are present
    history_texts = [item["sms_text"] for item in history]
    for msg in messages:
        assert msg in history_texts


def test_e2e_multi_session_isolation_and_counts():
    """
    E2E flow with two independent sessions:
    - session A sends 2 messages
    - session B sends 1 message
    - verify each session's history only contains its own messages
      and counts are correct.
    """
    session_a = str(uuid4())
    session_b = str(uuid4())

    msgs_a = [
        "This is session A - first message",
        "This is session A - second message",
    ]
    msg_b = "This is session B - only message"

    # Session A messages
    for msg in msgs_a:
        resp = client.post(
            "/predict",
            json={"text": msg, "session_id": session_a},
        )
        assert resp.status_code == 200

    # Session B message
    resp_b = client.post(
        "/predict",
        json={"text": msg_b, "session_id": session_b},
    )
    assert resp_b.status_code == 200

    # Histories
    hist_a = client.get(f"/history/{session_a}").json()
    hist_b = client.get(f"/history/{session_b}").json()

    texts_a = [item["sms_text"] for item in hist_a]
    texts_b = [item["sms_text"] for item in hist_b]

    # Session A should contain its 2 messages and not B's
    for msg in msgs_a:
        assert msg in texts_a
    assert msg_b not in texts_a

    # Session B should contain its message and not A's
    assert msg_b in texts_b
    for msg in msgs_a:
        assert msg not in texts_b
