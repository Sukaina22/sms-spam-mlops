from uuid import uuid4
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PredictRequest(BaseModel):
    text: str
    session_id: str | None = None  
    user_label: Optional[str] = None

    @classmethod
    def create(
        cls,
        text: str,
        session_id: str | None = None,
        user_label: str | None = None,
    ) -> "PredictRequest":
        return cls(
            text=text,
            session_id=session_id,
            user_label=user_label,
        )

class PredictResponse(BaseModel):
    label: str
    confidence: float
    session_id: str

    @classmethod
    def from_prediction(
        cls,
        label: str,
        confidence: float,
        session_id: str | None = None,
    ) -> "PredictResponse":
        return cls(
            label=label,
            confidence=round(confidence, 4),
            session_id=session_id or str(uuid4()),
        )

class HistoryItem(BaseModel):
    id: int
    sms_text: str
    label: str
    confidence: float
    created_at: Optional[str] = None
    user_label: Optional[str] = None

    @classmethod
    def from_db(cls, row):
        return cls(
            id=row.id,
            sms_text=row.sms_text,
            label=row.label,
            confidence=row.confidence,
            created_at=row.created_at.isoformat() if row.created_at else None,
            user_label=getattr(row, "user_label", None),
        )

class StatsResponse(BaseModel):
    total_predictions: int
    spam_count: int
    ham_count: int
    spam_rate: float
    last_24h_predictions: int
    unique_sessions: int
    with_user_label: int
    user_model_agreement: int
    user_model_disagreement: int

    @classmethod
    def from_counts(
        cls,
        *,
        total_predictions: int,
        spam_count: int,
        ham_count: int,
        last_24h_predictions: int,
        unique_sessions: int,
        with_user_label: int,
        user_model_agreement: int,
        user_model_disagreement: int,
    ) -> "StatsResponse":

        spam_rate = (
            spam_count / total_predictions
            if total_predictions > 0
            else 0.0
        )

        return cls(
            total_predictions=total_predictions,
            spam_count=spam_count,
            ham_count=ham_count,
            spam_rate=round(spam_rate, 4),
            last_24h_predictions=last_24h_predictions,
            unique_sessions=unique_sessions,
            with_user_label=with_user_label,
            user_model_agreement=user_model_agreement,
            user_model_disagreement=user_model_disagreement,
        )