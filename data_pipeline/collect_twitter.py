# تعليمي: جمع بيانات من Twitter/X يحتاج API رسمي وصلاحيات.
# هذا السكربت يوضح البنية العامة فقط ويحفظ ملف CSV تجريبي.
import argparse
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="sentiment")
    parser.add_argument("--out", default="twitter_sample.csv")
    args = parser.parse_args()

    rows = [
        {"text": "هذا المنتج رائع جدا", "source": "twitter", "query": args.query},
        {"text": "الخدمة سيئة وبطيئة", "source": "twitter", "query": args.query},
        {"text": "The app is good and useful", "source": "twitter", "query": args.query},
    ]
    pd.DataFrame(rows).to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"Saved {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
