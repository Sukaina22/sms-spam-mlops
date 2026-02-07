from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Tuple
import uuid
import dagshub
import mlflow
from app.dataTransfers import HistoryItem, PredictRequest, PredictResponse
import os
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models import Prediction
from fastapi import Depends
from sqlalchemy.orm import Session

DATABASE_URL = os.getenv("DATABASE_URL")
DAGSHUB_OWNER = "Sukaina22"
DAGSHUB_REPO = "sms-spam-mlops"
REGISTERED_MODEL_NAME = "sms_spam_classifier"
MODEL_URI = "models:/sms_spam_classifier/2"
MODEL_VERSION = os.getenv("MODEL_VERSION", "v2")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

app = FastAPI(title="SMS Spam Detector API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://sms-spam-detector.koyeb.app"
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

# ---------- ENDPOINTS ----------

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, db: Session = Depends(get_db),):
    session_id = request.session_id or str(uuid.uuid4())
    label, confidence = predict_sms(request.text)

    prediction = Prediction(
        session_id=session_id,
        sms_text=request.text,
        label=label,
        confidence=float(confidence),
        model_version=MODEL_VERSION,
        user_label=request.user_label,
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

@app.get("/history/{session_id}", response_model=List[HistoryItem])
def get_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
):
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
