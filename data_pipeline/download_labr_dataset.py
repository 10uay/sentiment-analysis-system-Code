from datasets import load_dataset
from pathlib import Path
import pandas as pd


OUT_DIR = Path("data_pipeline/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading LABR dataset...")
dataset = load_dataset("mohamedadaly/labr")

rows = []

for split_name, split_data in dataset.items():
    df = split_data.to_pandas()
    df["split"] = split_name

    print(f"\nSplit: {split_name}")
    print("Columns:", list(df.columns))
    print("Features:", split_data.features)
    print(df.head())

    rows.append(df)

full_df = pd.concat(rows, ignore_index=True)

print("\nAll columns:")
print(list(full_df.columns))

if "text" not in full_df.columns:
    raise ValueError(f"Could not find text column. Columns are: {list(full_df.columns)}")

if "label" not in full_df.columns:
    raise ValueError(f"Could not find label column. Columns are: {list(full_df.columns)}")

print("\nUnique label values:")
print(sorted(full_df["label"].dropna().unique()))

print("\nLabel distribution before mapping:")
print(full_df["label"].value_counts().sort_index())


def label_to_5class(label):
    """
    LABR قد يأتي بترميز 0-4 أو 1-5.
    إذا كان 0-4:
        0 -> very_negative
        1 -> negative
        2 -> neutral
        3 -> positive
        4 -> very_positive

    إذا كان 1-5:
        1 -> very_negative
        2 -> negative
        3 -> neutral
        4 -> positive
        5 -> very_positive
    """
    label = int(label)

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

    # في حال كانت القيم 1-5 بدل 0-4
    if label == 5:
        return "very_positive"

    raise ValueError(f"Unknown label value: {label}")


df = pd.DataFrame()
df["text"] = full_df["text"].astype(str)
df["original_label"] = full_df["label"].astype(int)
df["label"] = full_df["label"].apply(label_to_5class)
df["language"] = "ar"
df["source"] = "LABR"
df["split"] = full_df["split"]

df = df[df["text"].str.strip().str.len() > 0].copy()

print("\nMapped label distribution:")
print(df["label"].value_counts())

# موازنة البيانات: نأخذ عددًا متساويًا تقريبًا من كل فئة
MAX_PER_CLASS = 4000
balanced_parts = []

for label, group in df.groupby("label"):
    n = min(len(group), MAX_PER_CLASS)
    balanced_parts.append(group.sample(n=n, random_state=42))

balanced_df = pd.concat(balanced_parts, ignore_index=True)
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

# نحتفظ بالأعمدة المهمة للتدريب
balanced_df = balanced_df[["text", "label", "language", "source"]]

full_path = OUT_DIR / "labr_full_5class.csv"
balanced_path = OUT_DIR / "labr_5class_balanced.csv"

df.to_csv(full_path, index=False, encoding="utf-8-sig")
balanced_df.to_csv(balanced_path, index=False, encoding="utf-8-sig")

print("\nSaved full dataset to:", full_path)
print("Saved balanced dataset to:", balanced_path)

print("\nBalanced distribution:")
print(balanced_df["label"].value_counts())

print("\nFinal file preview:")
print(balanced_df.head())