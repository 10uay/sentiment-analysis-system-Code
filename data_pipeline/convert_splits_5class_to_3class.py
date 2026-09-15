from pathlib import Path
import pandas as pd


INPUT_DIR = Path("data_pipeline/processed/splits_5class")
OUTPUT_DIR = Path("data_pipeline/processed/splits_3class")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def to_3class(label):
    label = str(label).strip().lower()

    if label in ["very_negative", "negative"]:
        return "negative"

    if label == "neutral":
        return "neutral"

    if label in ["positive", "very_positive"]:
        return "positive"

    return None


for split_name in ["train", "validation", "test"]:
    input_path = INPUT_DIR / f"{split_name}.csv"
    output_path = OUTPUT_DIR / f"{split_name}.csv"

    df = pd.read_csv(input_path)

    df["label"] = df["label"].apply(to_3class)
    df = df.dropna(subset=["clean_text", "label"])
    df = df[df["clean_text"].astype(str).str.strip().str.len() > 0]

    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Saved: {output_path}")
    print(df["label"].value_counts())
    print()