from datasets import load_dataset
from pathlib import Path
import pandas as pd


DATASET_NAME = "tyqiangz/multilingual-sentiments"

CONFIGS = [
    ("arabic", "ar"),
    ("english", "en"),
]

OUT_DIR = Path("data_pipeline/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_PER_CLASS_PER_LANGUAGE = 2000  # يمكن زيادتها لاحقًا


def find_text_column(df):
    candidates = ["text", "sentence", "review", "content"]
    for col in candidates:
        if col in df.columns:
            return col
    raise ValueError(f"No text column found. Available columns: {list(df.columns)}")


def convert_label(value, dataset_split):
    label_feature = dataset_split.features.get("label")

    # إذا كان label مخزنًا كرقم وله أسماء داخل Hugging Face
    if hasattr(label_feature, "int2str"):
        try:
            return label_feature.int2str(int(value)).lower()
        except Exception:
            pass

    return str(value).strip().lower()


def normalize_label(label):
    label = str(label).strip().lower()

    mapping = {
        "positive": "positive",
        "pos": "positive",
        "1": "positive",

        "negative": "negative",
        "neg": "negative",
        "0": "negative",

        "neutral": "neutral",
        "neu": "neutral",
        "2": "neutral",
    }

    if label not in mapping:
        raise ValueError(f"Unknown label value: {label}")

    return mapping[label]


all_rows = []

for config_name, lang_code in CONFIGS:
    print(f"\nLoading config: {config_name}")

    dataset_dict = load_dataset(
        DATASET_NAME,
        config_name,
        trust_remote_code=True
    )

    for split_name, dataset_split in dataset_dict.items():
        print(f"Processing split: {config_name}/{split_name}")

        df = dataset_split.to_pandas()
        print("Columns:", list(df.columns))

        text_col = find_text_column(df)

        temp = pd.DataFrame()
        temp["text"] = df[text_col].astype(str)
        temp["label"] = df["label"].apply(lambda x: convert_label(x, dataset_split))
        temp["label"] = temp["label"].apply(normalize_label)
        temp["language"] = lang_code
        temp["split"] = split_name
        temp["source"] = DATASET_NAME

        all_rows.append(temp)

full_df = pd.concat(all_rows, ignore_index=True)

# حذف النصوص الفارغة
full_df = full_df.dropna(subset=["text", "label", "language"])
full_df = full_df[full_df["text"].str.strip().str.len() > 0]

# حفظ النسخة الكاملة
full_path = OUT_DIR / "hf_ar_en_sentiment_full.csv"
full_df.to_csv(full_path, index=False, encoding="utf-8-sig")

print("\nFull dataset saved to:")
print(full_path)
print("\nFull dataset size:")
print(len(full_df))
print("\nFull label/language distribution:")
print(full_df.groupby(["language", "label"]).size())

# إنشاء نسخة متوازنة ومناسبة للتدريب الأولي
balanced_parts = []

for (language, label), group in full_df.groupby(["language", "label"]):
    n = min(len(group), MAX_PER_CLASS_PER_LANGUAGE)
    balanced_parts.append(group.sample(n=n, random_state=42))

balanced_df = pd.concat(balanced_parts, ignore_index=True)
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

# نحتفظ بالأعمدة التي يحتاجها مشروعنا فقط
balanced_df = balanced_df[["text", "label", "language"]]

real_path = OUT_DIR / "real_dataset.csv"
balanced_df.to_csv(real_path, index=False, encoding="utf-8-sig")

print("\nBalanced training dataset saved to:")
print(real_path)
print("\nBalanced dataset size:")
print(len(balanced_df))
print("\nBalanced distribution:")
print(balanced_df.groupby(["language", "label"]).size())