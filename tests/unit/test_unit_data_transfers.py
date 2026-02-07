from app.dataTransfers import HistoryItem, PredictRequest, PredictResponse, StatsResponse
from types import SimpleNamespace

def test_predict_request_create():
    req = PredictRequest.create(
        text="Hello world",
        session_id="abc123",
        user_label="ham",
    )

    assert req.text == "Hello world"
    assert req.session_id == "abc123"
    assert req.user_label == "ham"

def test_predict_response_rounds_confidence_and_sets_session():
    resp = PredictResponse.from_prediction(
        label="spam",
        confidence=0.987654,
        session_id=None,
    )

    assert resp.label == "spam"
    assert resp.confidence == 0.9877
    assert resp.session_id is not None

from datetime import datetime

def test_history_item_from_db():
    now = datetime.utcnow()

    row = SimpleNamespace(
        id=1,
        sms_text="Win money now",
        label="spam",
        confidence=0.95,
        created_at=now,
        user_label=None,
    )

    item = HistoryItem.from_db(row)

    assert item.id == 1
    assert item.sms_text == "Win money now"
    assert item.label == "spam"
    assert item.confidence == 0.95
    assert item.created_at == now.isoformat()

def test_stats_response_spam_rate_calculation():
    stats = StatsResponse.from_counts(
        total_predictions=10,
        spam_count=4,
        ham_count=6,
        last_24h_predictions=3,
        unique_sessions=5,
        with_user_label=2,
        user_model_agreement=1,
        user_model_disagreement=1,
    )

    assert stats.spam_rate == 0.4

def test_stats_response_zero_predictions():
    stats = StatsResponse.from_counts(
        total_predictions=0,
        spam_count=0,
        ham_count=0,
        last_24h_predictions=0,
        unique_sessions=0,
        with_user_label=0,
        user_model_agreement=0,
        user_model_disagreement=0,
    )

    assert stats.spam_rate == 0.0
