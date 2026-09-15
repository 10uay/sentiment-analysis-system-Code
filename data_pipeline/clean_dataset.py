import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.preprocessor import TextPreprocessor  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--text-col", default="text")
    parser.add_argument("--out", default="clean_dataset.csv")
    args = parser.parse_args()

    pre = TextPreprocessor()
    df = pd.read_csv(args.input)
    df["clean_text"] = df[args.text_col].astype(str).apply(pre.clean)
    df["language"] = df["clean_text"].apply(pre.detect_language)
    df.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"Saved cleaned dataset to {args.out}")


if __name__ == "__main__":
    main()
