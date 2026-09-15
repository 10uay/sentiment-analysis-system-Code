import re
from pathlib import Path

import pandas as pd


INPUT_PATH = Path("data_pipeline/processed/real_clean.csv")
OUTPUT_PATH = Path("data_pipeline/processed/real_clean_v2.csv")


def replace_unicode_escape(match):
    """
    يحول فقط الرموز المكتوبة بشكل حرفي مثل \\u002c
    ولا يلمس النص العربي الطبيعي.
    """
    try:
        return chr(int(match.group(1), 16))
    except Exception:
        return " "


def clean_extra(text: str) -> str:
    text = str(text)

    # تحويل الرموز الحرفية من نوع \uXXXX فقط
    text = re.sub(r"\\u([0-9a-fA-F]{4})", replace_unicode_escape, text)

    # حذف الروابط
    text = re.sub(r"http\S+|www\S+", " ", text)

    # حذف RT في بداية التغريدات
    text = re.sub(r"\bRT\b", " ", text, flags=re.IGNORECASE)

    # حذف المنشن
    text = re.sub(r"@\w+", " ", text)

    # حذف إشارة الهاشتاغ مع إبقاء الكلمة
    text = text.replace("#", " ")

    # حذف الرموز غير المفيدة مع الحفاظ على العربية والإنكليزية والأرقام
    text = re.sub(r"[^\u0600-\u06FFa-zA-Z0-9\s\.\,\!\?\-\:؛،؟]", " ", text)

    # تقليل تكرار المسافات
    text = re.sub(r"\s+", " ", text).strip()

    return text


def main():
    df = pd.read_csv(INPUT_PATH)

    if "clean_text" not in df.columns:
        raise ValueError("clean_text column not found")

    if "label" not in df.columns:
        raise ValueError("label column not found")

    if "language" not in df.columns:
        raise ValueError("language column not found")

    before_count = len(df)
    before_ar = (df["language"] == "ar").sum()
    before_en = (df["language"] == "en").sum()

    df["clean_text"] = df["clean_text"].astype(str).apply(clean_extra)

    # حذف النصوص الفارغة فقط، وليس حذف العربية
    df = df[df["clean_text"].str.strip().str.len() >= 3].copy()

    # الاحتفاظ فقط بالفئات الثلاث المطلوبة
    df = df[df["label"].isin(["positive", "negative", "neutral"])].copy()

    # حذف التكرارات
    df = df.drop_duplicates(subset=["clean_text", "label", "language"]).copy()

    after_count = len(df)
    after_ar = (df["language"] == "ar").sum()
    after_en = (df["language"] == "en").sum()

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Saved cleaned dataset to: {OUTPUT_PATH}")
    print(f"Before cleaning: {before_count}")
    print(f"After cleaning:  {after_count}")

    print("\nLanguage count before:")
    print(f"Arabic:  {before_ar}")
    print(f"English: {before_en}")

    print("\nLanguage count after:")
    print(f"Arabic:  {after_ar}")
    print(f"English: {after_en}")

    print("\nDistribution after cleaning:")
    print(df.groupby(["language", "label"]).size())

    print("\nSample Arabic rows:")
    print(df[df["language"] == "ar"][["clean_text", "label"]].head(10))


if __name__ == "__main__":
    main()