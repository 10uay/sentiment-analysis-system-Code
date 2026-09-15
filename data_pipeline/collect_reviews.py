import argparse
from pathlib import Path
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=False)
    parser.add_argument("--out", default="reviews.csv")
    args = parser.parse_args()

    if args.input and Path(args.input).exists():
        df = pd.read_csv(args.input)
    else:
        df = pd.DataFrame([
            {"text": "Excellent service", "label": "positive"},
            {"text": "Bad experience", "label": "negative"},
            {"text": "الخدمة مقبولة", "label": "neutral"},
        ])

    df.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"Saved reviews to {args.out}")


if __name__ == "__main__":
    main()
