from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import mlflow
import mlflow.sklearn
import dagshub

# --- Configure MLflow to talk to DagsHub ---
dagshub.init(
    repo_owner="Sukaina22",          # <--- your DagsHub username
    repo_name="sms-spam-mlops",      # <--- your DagsHub repo name
    mlflow=True
)

MODEL_URI = "models:/sms_spam_classifier/1"

app = FastAPI(
    title="SMS Spam Detector API",
    version="1.0.0",
    description="Predict whether an SMS is ham or spam using the model from MLflow Model Registry on DagsHub."
)

class SMSRequest(BaseModel):
    text: str

class SMSResponse(BaseModel):
    label: str
    spam_probability: float

def load_model():
    # This loads the model directly from the MLflow registry
    return mlflow.sklearn.load_model(MODEL_URI)

# Load once when the app starts
model = load_model()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=SMSResponse)
def predict(request: SMSRequest):
    text = request.text

    # MLflow sklearn models expect a pandas DataFrame
    df = pd.DataFrame({"text": [text]})
    label = model.predict(df)[0]

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(df)[0]
        # Assuming your classes are ['ham', 'spam']
        spam_idx = list(model.classes_).index("spam")
        spam_prob = float(proba[spam_idx])
    else:
        spam_prob = 0.0

    return SMSResponse(label=label, spam_probability=spam_prob)
