import os
import pandas as pd

RAW_DATA_PATH = "data/raw/spam.csv"
PROCESSED_DATA_PATH = "data/processed/sms_spam_clean.csv"


def main():
    df = pd.read_csv(RAW_DATA_PATH)

    df = df.rename(columns={
        "v1": "label",
        "v2": "text"
    })

    df = df[["label", "text"]]

    df = df.dropna(subset=["label", "text"])

    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)

    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"Processed dataset saved to: {PROCESSED_DATA_PATH}")
    print(f"Final dataset shape: {df.shape}")


if __name__ == "__main__":
    main()
