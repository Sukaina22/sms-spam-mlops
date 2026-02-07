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


def test_predict_returns_label_and_probability():
    session_id = str(uuid4())
    payload = {
        "text": "FREE FREE FREE! You have won a $1000 gift card.",
        "session_id": session_id,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200

    data = response.json()

    assert "label" in data
    assert "confidence" in data
    assert "session_id" in data

    assert data["label"] in ("spam", "ham")
    assert 0.0 <= float(data["confidence"]) <= 1.0


def test_predict_creates_history_entry():
    session_id = str(uuid4())
    sms_text = "Hey, I'll be late today. Let's meet around 7pm instead."

    resp_predict = client.post(
        "/predict",
        json={"text": sms_text, "session_id": session_id},
    )
    assert resp_predict.status_code == 200

    resp_history = client.get(f"/history/{session_id}")
    assert resp_history.status_code == 200

    history = resp_history.json()
    assert isinstance(history, list)
    assert len(history) >= 1

    assert any(item["sms_text"] == sms_text for item in history)


def test_history_is_isolated_per_session():
    session_a = str(uuid4())
    session_b = str(uuid4())

    sms_a = "Message for session A only."
    sms_b = "Message for session B only."

    resp_a = client.post(
        "/predict",
        json={"text": sms_a, "session_id": session_a},
    )
    assert resp_a.status_code == 200

    resp_b = client.post(
        "/predict",
        json={"text": sms_b, "session_id": session_b},
    )
    assert resp_b.status_code == 200

    history_a = client.get(f"/history/{session_a}").json()
    history_b = client.get(f"/history/{session_b}").json()

    assert any(item["sms_text"] == sms_a for item in history_a)
    assert all(item["sms_text"] != sms_b for item in history_a)

    assert any(item["sms_text"] == sms_b for item in history_b)
    assert all(item["sms_text"] != sms_a for item in history_b)
