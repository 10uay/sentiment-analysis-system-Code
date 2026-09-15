import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.embedding_service import EmbeddingService  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--text-col", default="text")
    parser.add_argument("--out", default="vector_index.json")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    service = EmbeddingService()
    items = []
    for i, row in df.iterrows():
        text = str(row[args.text_col])
        items.append({
            "id": int(i),
            "text": text,
            "metadata": {k: str(v) for k, v in row.items() if k != args.text_col},
            "embedding": service.embed(text),
        })

    service.save_index(items, args.out)
    print(f"Saved vector index with {len(items)} items to {args.out}")


if __name__ == "__main__":
    main()
