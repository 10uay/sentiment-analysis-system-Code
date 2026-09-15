import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "training" / "outputs"

WITH_RAG_PATH = OUTPUT_DIR / "api_with_rag_metrics.json"
WITHOUT_RAG_PATH = OUTPUT_DIR / "api_without_rag_metrics.json"


def load_metrics(path: Path, experiment_name: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "experiment": experiment_name,
        "model": data.get("model"),
        "use_rag": data.get("use_rag"),
        "total_samples": data.get("total_samples"),
        "accuracy": data.get("accuracy"),
        "weighted_precision": data.get("weighted_precision"),
        "weighted_recall": data.get("weighted_recall"),
        "weighted_f1": data.get("weighted_f1"),
        "macro_precision": data.get("macro_precision"),
        "macro_recall": data.get("macro_recall"),
        "macro_f1": data.get("macro_f1"),
        "total_runtime_seconds": data.get("total_runtime_seconds"),
        "average_runtime_per_sample_seconds": data.get("average_runtime_per_sample_seconds"),
    }


def main():
    rows = [
        load_metrics(WITHOUT_RAG_PATH, "Ensemble without RAG"),
        load_metrics(WITH_RAG_PATH, "Ensemble with RAG"),
    ]

    df = pd.DataFrame(rows)

    # حساب الفرق بين RAG وبدون RAG
    without = df[df["use_rag"] == False].iloc[0]
    with_rag = df[df["use_rag"] == True].iloc[0]

    delta_row = {
        "experiment": "Difference: with RAG - without RAG",
        "model": "ensemble",
        "use_rag": "delta",
        "total_samples": with_rag["total_samples"],
        "accuracy": with_rag["accuracy"] - without["accuracy"],
        "weighted_precision": with_rag["weighted_precision"] - without["weighted_precision"],
        "weighted_recall": with_rag["weighted_recall"] - without["weighted_recall"],
        "weighted_f1": with_rag["weighted_f1"] - without["weighted_f1"],
        "macro_precision": with_rag["macro_precision"] - without["macro_precision"],
        "macro_recall": with_rag["macro_recall"] - without["macro_recall"],
        "macro_f1": with_rag["macro_f1"] - without["macro_f1"],
        "total_runtime_seconds": with_rag["total_runtime_seconds"] - without["total_runtime_seconds"],
        "average_runtime_per_sample_seconds": (
            with_rag["average_runtime_per_sample_seconds"]
            - without["average_runtime_per_sample_seconds"]
        ),
    }

    df = pd.concat([df, pd.DataFrame([delta_row])], ignore_index=True)

    out_csv = OUTPUT_DIR / "api_rag_comparison_summary.csv"
    out_md = OUTPUT_DIR / "api_rag_comparison_summary.md"

    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# API Evaluation: RAG vs Without RAG\n\n")
        f.write(df.to_markdown(index=False))

    print("\nComparison summary:")
    print(df)

    print(f"\nSaved CSV summary to: {out_csv}")
    print(f"Saved Markdown summary to: {out_md}")


if __name__ == "__main__":
    main()