from pathlib import Path
import pandas as pd


RAW_DIR = Path("data_pipeline/raw")
OUT_PATH = RAW_DIR / "ar_en_5class_dataset.csv"

ar_path = RAW_DIR / "labr_5class_balanced.csv"
en_path = RAW_DIR / "sst5_5class_balanced.csv"

ar_df = pd.read_csv(ar_path)
en_df = pd.read_csv(en_path)

# نحتفظ فقط بالأعمدة المشتركة
cols = ["text", "label", "language", "source"]

ar_df = ar_df[cols]
en_df = en_df[cols]

df = pd.concat([ar_df, en_df], ignore_index=True)
df = df.dropna(subset=["text", "label", "language"])
df = df[df["text"].astype(str).str.strip().str.len() > 0]
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print("Saved merged dataset to:", OUT_PATH)
print("Total samples:", len(df))
print("\nDistribution:")
print(df.groupby(["language", "label"]).size())