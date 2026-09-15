from pathlib import Path
import pandas as pd


SPLIT_DIR = Path("data_pipeline/processed/splits_5class")
OUT_PATH = Path("data_pipeline/processed/rag_train_val_5class.csv")

train_df = pd.read_csv(SPLIT_DIR / "train.csv")
val_df = pd.read_csv(SPLIT_DIR / "validation.csv")

df = pd.concat([train_df, val_df], ignore_index=True)

df = df.dropna(subset=["clean_text", "label"])
df = df[df["clean_text"].astype(str).str.strip().str.len() > 0]
df = df.drop_duplicates(subset=["clean_text", "label"])

df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print("Saved RAG dataset to:", OUT_PATH)
print("Total samples:", len(df))
print("\nDistribution:")
print(df["label"].value_counts())