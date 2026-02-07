import os
import sys
from uuid import uuid4

from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(__file__)
TESTS_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(TESTS_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import app

client = TestClient(app)


def test_e2e_spam_flow_predict_then_history():
    session_id = str(uuid4())
    sms_text = "FREE FREE FREE! You have won a $1000 gift card. Click now!"

    resp_predict = client.post(
        "/predict",
        json={"text": sms_text, "session_id": session_id},
    )
    assert resp_predict.status_code == 200

    data = resp_predict.json()
    assert data["label"] in ("spam", "ham")
    assert 0.0 <= float(data["confidence"]) <= 1.0
    assert data["session_id"] == session_id

    resp_history = client.get(f"/history/{session_id}")
    assert resp_history.status_code == 200

    history = resp_history.json()
    assert isinstance(history, list)
    assert len(history) >= 1

    assert any(
        item["sms_text"] == sms_text and item["label"] == data["label"]
        for item in history
    )


def test_e2e_multiple_messages_single_session():
    session_id = str(uuid4())
    messages = [
        "Hey, are we still on for tonight?",
        "Reminder: Your invoice is due tomorrow.",
        "WIN a brand new iPhone by clicking this link!",
    ]

    for msg in messages:
        resp = client.post(
            "/predict",
            json={"text": msg, "session_id": session_id},
        )
        assert resp.status_code == 200

    resp_history = client.get(f"/history/{session_id}")
    assert resp_history.status_code == 200

    history = resp_history.json()
    assert isinstance(history, list)
    assert len(history) >= len(messages)

    history_texts = [item["sms_text"] for item in history]
    for msg in messages:
        assert msg in history_texts


def test_e2e_multi_session_isolation_and_counts():
    session_a = str(uuid4())
    session_b = str(uuid4())

    msgs_a = [
        "Claim your lottery prize before it expires. Call +44 7700 900123",
        "I'll call you when I arrive.",
    ]
    msg_b = "You've been shortlisted. Pay registration fee to proceed."

    for msg in msgs_a:
        resp = client.post(
            "/predict",
            json={"text": msg, "session_id": session_a},
        )
        assert resp.status_code == 200

    resp_b = client.post(
        "/predict",
        json={"text": msg_b, "session_id": session_b},
    )
    assert resp_b.status_code == 200

    hist_a = client.get(f"/history/{session_a}").json()
    hist_b = client.get(f"/history/{session_b}").json()

    texts_a = [item["sms_text"] for item in hist_a]
    texts_b = [item["sms_text"] for item in hist_b]

    for msg in msgs_a:
        assert msg in texts_a
    assert msg_b not in texts_a

    assert msg_b in texts_b
    for msg in msgs_a:
        assert msg not in texts_b
