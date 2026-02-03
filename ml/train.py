import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


# Use the CLEANED dataset produced by prepare_raw_data.py
DATA_PATH = "data/processed/sms_spam_clean.csv"

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "baseline_spam_model.joblib")


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


def build_model() -> Pipeline:
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
                    max_features=5000,  # limit vocab size for speed
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )

    return pipeline


def evaluate_model(model: Pipeline, X_test, y_test) -> None:
    """Print accuracy, precision, recall and F1 on the test set."""
    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, preds, average="binary", pos_label="spam"
    )

    print("\n=== Evaluation on test set ===")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")


def main():
    print("Loading data...")
    df = load_data(DATA_PATH)
    print(f"Dataset shape: {df.shape}")

    # Features & labels
    X = df["text"]
    y = df["label"]  # 'ham' or 'spam'

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,  # keep spam/ham ratio
    )

    print("Building model...")
    model = build_model()

    print("Training model...")
    model.fit(X_train, y_train)

    print("Evaluating model...")
    evaluate_model(model, X_test, y_test)

    # Save the trained pipeline (vectorizer + classifier together)
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
