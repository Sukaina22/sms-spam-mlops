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
    user_label = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    used_for_training = Column(Boolean, nullable=False, default=False)