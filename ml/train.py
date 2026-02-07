import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
)

import dagshub
import mlflow
import mlflow.sklearn

DAGSHUB_OWNER = "Sukaina22"
DAGSHUB_REPO = "sms-spam-mlops"
DATA_PATH = "data/processed/sms_spam_clean.csv"
EXPERIMENT_NAME = "sms-spam-baseline"
REGISTERED_MODEL_NAME = "sms_spam_classifier"
TEST_SIZE = 0.2
RANDOM_STATE = 42
MAX_FEATURES = 5000
MAX_ITER = 1000

def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at {path}. "
            "Did you run ml/prepare_raw_data.py and dvc pull?"
        )

    df = pd.read_csv(path)

    expected_cols = {"label", "text"}
    if not expected_cols.issubset(df.columns):
        raise ValueError(
            f"Dataset must contain columns {expected_cols}, "
            f"found {df.columns.tolist()}"
        )

    df = df.dropna(subset=["label", "text"])
    return df


def build_model(
    max_features: int = MAX_FEATURES,
    max_iter: int = MAX_ITER,
) -> Pipeline:
    pipeline = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    stop_words="english",
                    max_features=max_features,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=max_iter,
                    random_state=RANDOM_STATE,
                    class_weight="balanced",
                ),
            ),
        ]
    )
    return pipeline


def evaluate_model(model: Pipeline, X_test, y_test):
    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, preds, average="binary", pos_label="spam"
    )

    return acc, precision, recall, f1

def main():
    dagshub.init(
        repo_owner=DAGSHUB_OWNER,
        repo_name=DAGSHUB_REPO,
        mlflow=True,
    )

    mlflow.set_experiment(EXPERIMENT_NAME)

    print("Loading data...")
    df = load_data(DATA_PATH)
    print(f"Dataset shape: {df.shape}")

    X = df["text"]
    y = df["label"]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    print("Building model...")
    model = build_model()

    print("Training model...")
    model.fit(X_train, y_train)

    print("Evaluating model...")
    acc, precision, recall, f1 = evaluate_model(model, X_test, y_test)

    print("\n=== Evaluation on test set ===")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")

    with mlflow.start_run():
        mlflow.log_param("model_type", "logreg_tfidf")
        mlflow.log_param("test_size", TEST_SIZE)
        mlflow.log_param("max_features", MAX_FEATURES)
        mlflow.log_param("max_iter", MAX_ITER)
        mlflow.log_param("dataset_rows", len(df))

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1", f1)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=REGISTERED_MODEL_NAME,
        )

    print("\nTraining + MLflow logging complete.")


if __name__ == "__main__":
    main()
