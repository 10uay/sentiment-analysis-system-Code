import argparse
import pandas as pd

POS = {"good", "great", "excellent", "love", "رائع", "ممتاز", "جيد"}
NEG = {"bad", "terrible", "hate", "worst", "سيء", "مشكله", "ضعيف"}


def weak_label(text: str) -> str:
    words = set(str(text).lower().split())
    pos = len(words & POS)
    neg = len(words & NEG)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--text-col", default="clean_text")
    parser.add_argument("--out", default="labeled_dataset.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    df["label"] = df[args.text_col].apply(weak_label)
    df.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"Saved weakly labeled dataset to {args.out}")


if __name__ == "__main__":
    main()
