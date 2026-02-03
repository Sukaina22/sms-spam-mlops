import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

import mlflow
import mlflow.sklearn


# Use the CLEANED dataset produced by prepare_raw_data.py
DATA_PATH = "data/processed/sms_spam_clean.csv"

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "baseline_spam_model.joblib")

EXPERIMENT_NAME = "sms-spam-baseline"


def load_data(path: str) -> pd.DataFrame:
    """Load the cleaned SMS spam dataset and do basic sanity checks."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at {path}. "
            "Did you run ml/prepare_raw_data.py and dvc pull?"
        )

    df = pd.read_csv(path)

    # Required columns
    expected_cols = {"label", "text"}
    if not expected_cols.issubset(df.columns):
        raise ValueError(
            f"Dataset must contain columns {expected_cols}, "
            f"found {df.columns.tolist()}"
        )

    # Drop any remaining missing values just in case
    df = df.dropna(subset=["label", "text"])

    return df


def build_model(max_features: int = 5000, max_iter: int = 1000) -> Pipeline:
    """
    Build a simple baseline model:

    - TfidfVectorizer converts SMS text into numeric features.
    - LogisticRegression does binary classification (ham vs spam).
    """
    pipeline = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    stop_words="english",
                    max_features=max_features,  # limit vocab size for speed
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=max_iter,
                    random_state=42,
                ),
            ),
        ]
    )

    return pipeline


def evaluate_model(model: Pipeline, X_test, y_test):
    """Return accuracy, precision, recall and F1 on the test set."""
    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, preds, average="binary", pos_label="spam"
    )

    return acc, precision, recall, f1


def main():
    print("Loading data...")
    df = load_data(DATA_PATH)
    print(f"Dataset shape: {df.shape}")

    # Features & labels
    X = df["text"]
    y = df["label"]  # 'ham' or 'spam'

    test_size = 0.2
    max_features = 5000
    max_iter = 1000

    # Set up / create experiment (local MLflow by default)
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("model_type", "logreg_tfidf")
        mlflow.log_param("test_size", test_size)
        mlflow.log_param("max_features", max_features)
        mlflow.log_param("max_iter", max_iter)
        mlflow.log_param("dataset_rows", len(df))

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=42,
            stratify=y,  # keep spam/ham ratio
        )

        print("Building model...")
        model = build_model(max_features=max_features, max_iter=max_iter)

        print("Training model...")
        model.fit(X_train, y_train)

        print("Evaluating model...")
        acc, precision, recall, f1 = evaluate_model(model, X_test, y_test)

        print("\n=== Evaluation on test set ===")
        print(f"Accuracy : {acc:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall   : {recall:.4f}")
        print(f"F1-score : {f1:.4f}")

        # Log metrics to MLflow
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1", f1)

        # Log model to MLflow (pipeline: vectorizer + classifier)
        mlflow.sklearn.log_model(model, artifact_path="model")

        # Also save to local models/ for FastAPI
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
