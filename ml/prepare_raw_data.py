import pandas as pd

df = pd.read_csv("data/raw/spam.csv", encoding="latin-1")

df = df.rename(columns={
    "v1": "label",
    "v2": "text"
})

df = df[["label", "text"]]

df.to_csv("data/raw/spam.csv", index=False)

print("Dataset cleaned and columns renamed to: label, text")
