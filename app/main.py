# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Tuple
from datetime import datetime
#import sqlite3
from contextlib import contextmanager
import uuid
import dagshub
import mlflow
from ml.utils import ensure_session_id
import os
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models import Prediction
from fastapi import Depends
from sqlalchemy.orm import Session



DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#DB_PATH = "sms_history.db"
DAGSHUB_OWNER = "Sukaina22"
DAGSHUB_REPO = "sms-spam-mlops"
REGISTERED_MODEL_NAME = "sms_spam_classifier"
MODEL_URI = "models:/sms_spam_classifier/2"

DATABASE_URL = os.getenv("DATABASE_URL")
# ---------- MODEL LOADING (PUT YOUR EXISTING CODE HERE) ----------

def load_model():
    token = os.getenv("DAGSHUB_TOKEN")
    if token:
        dagshub.auth.add_app_token(token)
    dagshub.init(
        repo_owner=DAGSHUB_OWNER,
        repo_name=DAGSHUB_REPO,
        mlflow=True,
    )

    print(f">>> Loading model from MLflow URI: {MODEL_URI}")
    model = mlflow.sklearn.load_model(MODEL_URI)
    print(">>> Model loaded:", type(model))
    print(">>> Classes:", getattr(model, "classes_", "no classes_ attr"))
    return model


model = load_model()



def predict_sms(text: str) -> Tuple[str, float]:
    X = [text]

    label = model.predict(X)[0]

    spam_prob = 0.0
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        classes = list(model.classes_)
        if "spam" in classes:
            spam_idx = classes.index("spam")
            spam_prob = float(proba[spam_idx])

    return label, spam_prob



# ---------- SQLITE HELPERS ----------

# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
#     cur.execute(
#         """
#         CREATE TABLE IF NOT EXISTS predictions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             session_id TEXT NOT NULL,
#             sms_text TEXT NOT NULL,
#             label TEXT NOT NULL,
#             confidence REAL NOT NULL,
#             created_at TEXT NOT NULL
#         )
#         """
#     )
#     conn.commit()
#     conn.close()


# @contextmanager
# def get_db():
#     conn = sqlite3.connect(DB_PATH)
#     try:
#         yield conn
#     finally:
#         conn.close()


# ---------- FASTAPI APP ----------

app = FastAPI(title="SMS Spam Detector API")

# CORS so Next.js (localhost:3000) can call FastAPI (e.g. localhost:8000)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# ---------- SCHEMAS ----------

class PredictRequest(BaseModel):
    text: str
    session_id: str | None = None  # frontend may omit

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



# ---------- ENDPOINTS ----------

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, db: Session = Depends(get_db),):
    # Ensure we have a session_id
    session_id = request.session_id or str(uuid.uuid4())
    #session_id = ensure_session_id(request.session_id)


    # Run your model
    label, confidence = predict_sms(request.text)

    # Store in DB
    # with get_db() as conn:
    #     cur = conn.cursor()
    #     cur.execute(
    #         """
    #         INSERT INTO predictions (session_id, sms_text, label, confidence, created_at)
    #         VALUES (?, ?, ?, ?, ?)
    #         """,
    #         (
    #             session_id,
    #             request.text,
    #             label,
    #             float(confidence),
    #             datetime.utcnow().isoformat(),
    #         ),
    #     )
    #     conn.commit()

    prediction = Prediction(
    session_id=session_id,
    sms_text=request.text,
    label=label,
    confidence=float(confidence),
)

    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    db.close()


    return PredictResponse(
        label=label,
        confidence=float(confidence),
        session_id=session_id,
    )


# @app.get("/history/{session_id}", response_model=List[HistoryItem])
# def get_history(session_id: str, limit: int = 50):
#     with get_db() as conn:
#         cur = conn.cursor()
#         cur.execute(
#             """
#             SELECT id, sms_text, label, confidence, created_at
#             FROM predictions
#             WHERE session_id = ?
#             ORDER BY id DESC
#             LIMIT ?
#             """,
#             (session_id, limit),
#         )
#         rows = cur.fetchall()

#     history: List[HistoryItem] = []
#     for row in rows:
#         id_, sms_text, label, confidence, created_at = row
#         history.append(
#             HistoryItem(
#                 id=id_,
#                 sms_text=sms_text,
#                 label=label,
#                 confidence=float(confidence),
#                 created_at=datetime.fromisoformat(created_at),
#             )
#         )
#     return history

@app.get("/history/{session_id}", response_model=List[HistoryItem])
def get_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    # Query Supabase/Postgres via SQLAlchemy
    rows = (
        db.query(Prediction)
        .filter(Prediction.session_id == session_id)
        .order_by(Prediction.id.desc())
        .limit(limit)
        .all()
    )

    history: List[HistoryItem] = []
    for row in rows:
        history.append(
            HistoryItem(
                id=row.id,
                sms_text=row.sms_text,
                label=row.label,
                confidence=row.confidence,
                created_at=row.created_at.isoformat() if row.created_at else None,
            )
        )

    return history
