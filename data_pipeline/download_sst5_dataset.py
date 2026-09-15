from datasets import load_dataset
from pathlib import Path
import pandas as pd


OUT_DIR = Path("data_pipeline/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading SST-5 dataset...")
dataset = load_dataset("SetFit/sst5")

rows = []

for split_name, split_data in dataset.items():
    df = split_data.to_pandas()
    df["split"] = split_name

    print(f"\nSplit: {split_name}")
    print("Columns:", list(df.columns))
    print(split_data.features)
    print(df.head())

    rows.append(df)

full_df = pd.concat(rows, ignore_index=True)

print("\nAll columns:")
print(list(full_df.columns))
print("\nLabel distribution:")
print(full_df["label"].value_counts().sort_index())


def label_to_5class(label):
    label = int(label)

    # في SST-5 غالبًا:
    # 0 very negative
    # 1 negative
    # 2 neutral
    # 3 positive
    # 4 very positive
    if label == 0:
        return "very_negative"
    if label == 1:
        return "negative"
    if label == 2:
        return "neutral"
    if label == 3:
        return "positive"
    if label == 4:
        return "very_positive"

    raise ValueError(f"Unknown label: {label}")


# غالبًا عمود النص اسمه text
text_col = "text"
if text_col not in full_df.columns:
    raise ValueError(f"text column not found. Columns: {list(full_df.columns)}")

df = pd.DataFrame()
df["text"] = full_df[text_col].astype(str)
df["original_label"] = full_df["label"].astype(int)
df["label"] = full_df["label"].apply(label_to_5class)
df["language"] = "en"
df["source"] = "SST5"
df["split"] = full_df["split"]

df = df[df["text"].str.strip().str.len() > 0].copy()

# موازنة أولية
MAX_PER_CLASS = 4000
balanced_parts = []

for label, group in df.groupby("label"):
    n = min(len(group), MAX_PER_CLASS)
    balanced_parts.append(group.sample(n=n, random_state=42))

balanced_df = pd.concat(balanced_parts, ignore_index=True)
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

balanced_df = balanced_df[["text", "label", "language", "source"]]

full_path = OUT_DIR / "sst5_full_5class.csv"
balanced_path = OUT_DIR / "sst5_5class_balanced.csv"

df.to_csv(full_path, index=False, encoding="utf-8-sig")
balanced_df.to_csv(balanced_path, index=False, encoding="utf-8-sig")

print("\nSaved full dataset to:", full_path)
print("Saved balanced dataset to:", balanced_path)

print("\nBalanced distribution:")
print(balanced_df["label"].value_counts())