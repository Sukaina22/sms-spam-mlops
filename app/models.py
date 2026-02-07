from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    sms_text = Column(String, nullable=False)
    label = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 👇 NEW FIELDS FOR OFFLINE RETRAINING
    # ground-truth label (optional, you’ll fill it later manually or via an admin UI)
    user_label = Column(String, nullable=True)

    # which model produced this prediction (e.g. "v1", "2", "2026-02-06")
    model_version = Column(String, nullable=True)

    # whether this row has already been used in an offline retraining job
    used_for_training = Column(Boolean, nullable=False, default=False)