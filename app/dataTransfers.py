from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PredictRequest(BaseModel):
    text: str
    session_id: str | None = None  
    user_label: Optional[str] = None

class PredictResponse(BaseModel):
    label: str
    confidence: float
    session_id: str

class HistoryItem(BaseModel):
    id: int
    sms_text: str
    label: str
    confidence: float
    created_at: datetime