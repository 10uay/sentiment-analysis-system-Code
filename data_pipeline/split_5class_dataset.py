from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


INPUT_PATH = Path("data_pipeline/processed/ar_en_5class_clean.csv")
OUTPUT_DIR = Path("data_pipeline/processed/splits_5class")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LABELS = [
    "very_negative",
    "negative",
    "neutral",
    "positive",
    "very_positive",
]


def fix_language(row):
    """
    لأن clean_dataset.py قد يكتشف اللغة بشكل خاطئ في بعض النصوص،
    نعيد ضبط اللغة اعتمادًا على مصدر البيانات.
    """
    source = str(row.get("source", "")).lower()

    if "labr" in source:
        return "ar"

    if "sst" in source:
        return "en"

    lang = str(row.get("language", "")).lower()

    if lang in ["ar", "arabic"]:
        return "ar"

    if lang in ["en", "english"]:
        return "en"

    return lang


def main():
    print(f"Reading dataset from: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    required_cols = {"clean_text", "label"}
    missing = required_cols - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    before = len(df)

    # الاحتفاظ بالفئات الخمس فقط
    df = df[df["label"].isin(LABELS)].copy()

    # حذف النصوص الفارغة
    df = df[df["clean_text"].astype(str).str.strip().str.len() > 0].copy()

    # تصحيح عمود اللغة
    df["language"] = df.apply(fix_language, axis=1)

    # الاحتفاظ بالعربي والإنكليزي فقط
    df = df[df["language"].isin(["ar", "en"])].copy()

    # حذف التكرارات لتقليل تسرب البيانات بين train و test
    df = df.drop_duplicates(subset=["clean_text"]).copy()

    after = len(df)

    print(f"Samples before filtering: {before}")
    print(f"Samples after filtering/deduplication: {after}")

    print("\nFull distribution by label:")
    print(df["label"].value_counts())

    print("\nFull distribution by language and label:")
    print(df.groupby(["language", "label"]).size())

    # التقسيم حسب label فقط لتجنب مشكلة المجموعات الصغيرة الناتجة عن كشف اللغة
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["label"],
    )

    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["label"],
    )

    train_path = OUTPUT_DIR / "train.csv"
    validation_path = OUTPUT_DIR / "validation.csv"
    test_path = OUTPUT_DIR / "test.csv"

    train_df.to_csv(train_path, index=False, encoding="utf-8-sig")
    validation_df.to_csv(validation_path, index=False, encoding="utf-8-sig")
    test_df.to_csv(test_path, index=False, encoding="utf-8-sig")

    print("\nSaved splits:")
    print(f"Train:      {train_path} -> {len(train_df)} samples")
    print(f"Validation: {validation_path} -> {len(validation_df)} samples")
    print(f"Test:       {test_path} -> {len(test_df)} samples")

    print("\nTrain distribution:")
    print(train_df["label"].value_counts())

    print("\nValidation distribution:")
    print(validation_df["label"].value_counts())

    print("\nTest distribution:")
    print(test_df["label"].value_counts())

    print("\nTrain language distribution:")
    print(train_df["language"].value_counts())

    print("\nValidation language distribution:")
    print(validation_df["language"].value_counts())

    print("\nTest language distribution:")
    print(test_df["language"].value_counts())


if __name__ == "__main__":
    main()