import argparse
import json
import time
from pathlib import Path

import pandas as pd
import requests
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)


LABELS = ["negative", "neutral", "positive"]


def normalize_label(value):
    if value is None:
        return "unknown"

    value = str(value).strip().lower()

    mapping = {
        "positive": "positive",
        "pos": "positive",
        "إيجابي": "positive",
        "ايجابي": "positive",

        "negative": "negative",
        "neg": "negative",
        "سلبي": "negative",

        "neutral": "neutral",
        "neu": "neutral",
        "محايد": "neutral",
        "حيادي": "neutral",
    }

    return mapping.get(value, value)


def find_value_recursive(obj, keys):
    """
    يبحث داخل JSON عن أول مفتاح مناسب مثل sentiment أو label أو confidence.
    """
    if isinstance(obj, dict):
        for key in keys:
            if key in obj:
                return obj[key]

        for value in obj.values():
            found = find_value_recursive(value, keys)
            if found is not None:
                return found

    elif isinstance(obj, list):
        for item in obj:
            found = find_value_recursive(item, keys)
            if found is not None:
                return found

    return None


def extract_prediction(response_json):
    keys = [
        "sentiment",
        "label",
        "prediction",
        "predicted_label",
        "final_sentiment",
        "result",
    ]
    return normalize_label(find_value_recursive(response_json, keys))


def extract_confidence(response_json):
    keys = [
        "confidence",
        "score",
        "probability",
        "final_confidence",
    ]

    value = find_value_recursive(response_json, keys)

    try:
        return float(value)
    except Exception:
        return None


def call_api(api_url, text, model, use_rag):
    payload = {
        "text": text,
        "model": model,
        "use_rag": use_rag,
    }

    response = requests.post(api_url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--text-col", default="clean_text")
    parser.add_argument("--label-col", default="label")
    parser.add_argument("--model", default="ensemble")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000/api/v1/analyze")
    parser.add_argument("--use-rag", action="store_true")
    parser.add_argument("--out-prefix", default="api_rag")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "training" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.data)

    if args.text_col not in df.columns:
        raise ValueError(f"Missing text column: {args.text_col}")

    if args.label_col not in df.columns:
        raise ValueError(f"Missing label column: {args.label_col}")

    rows = []
    y_true = []
    y_pred = []

    start_time = time.time()

    for idx, row in df.iterrows():
        text = str(row[args.text_col])
        true_label = normalize_label(row[args.label_col])

        print(f"[{idx + 1}/{len(df)}] {text[:80]}")

        try:
            response_json = call_api(
                api_url=args.api_url,
                text=text,
                model=args.model,
                use_rag=args.use_rag,
            )

            pred_label = extract_prediction(response_json)
            confidence = extract_confidence(response_json)
            error = ""

        except Exception as exc:
            response_json = {}
            pred_label = "error"
            confidence = None
            error = str(exc)

        y_true.append(true_label)
        y_pred.append(pred_label)

        rows.append({
            "text": row.get("text", text),
            "clean_text": text,
            "true_label": true_label,
            "predicted_label": pred_label,
            "confidence": confidence,
            "is_correct": true_label == pred_label,
            "model": args.model,
            "use_rag": args.use_rag,
            "error": error,
            "raw_response": json.dumps(response_json, ensure_ascii=False),
        })

    total_time = time.time() - start_time

    results_df = pd.DataFrame(rows)

    results_path = output_dir / f"{args.out_prefix}_results.csv"
    metrics_path = output_dir / f"{args.out_prefix}_metrics.json"
    report_path = output_dir / f"{args.out_prefix}_classification_report.txt"
    cm_path = output_dir / f"{args.out_prefix}_confusion_matrix.csv"

    results_df.to_csv(results_path, index=False, encoding="utf-8-sig")

    accuracy = accuracy_score(y_true, y_pred)

    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=LABELS,
        average="weighted",
        zero_division=0,
    )

    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=LABELS,
        average="macro",
        zero_division=0,
    )

    cm = confusion_matrix(y_true, y_pred, labels=LABELS)
    cm_df = pd.DataFrame(cm, index=LABELS, columns=LABELS)
    cm_df.to_csv(cm_path, encoding="utf-8-sig")

    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        zero_division=0,
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    metrics = {
        "model": args.model,
        "use_rag": args.use_rag,
        "total_samples": len(df),
        "accuracy": accuracy,
        "weighted_precision": weighted_precision,
        "weighted_recall": weighted_recall,
        "weighted_f1": weighted_f1,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "total_runtime_seconds": total_time,
        "average_runtime_per_sample_seconds": total_time / len(df),
        "labels": LABELS,
        "confusion_matrix": cm.tolist(),
    }

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("\nEvaluation finished.")
    print(f"Results: {results_path}")
    print(f"Metrics: {metrics_path}")
    print(f"Report: {report_path}")
    print(f"Confusion matrix: {cm_path}")

    print("\nMain Metrics:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Weighted Precision: {weighted_precision:.4f}")
    print(f"Weighted Recall: {weighted_recall:.4f}")
    print(f"Weighted F1-score: {weighted_f1:.4f}")
    print(f"Macro F1-score: {macro_f1:.4f}")
    print(f"Total runtime: {total_time:.2f} seconds")
    print(f"Average runtime/sample: {total_time / len(df):.4f} seconds")

    print("\nConfusion Matrix:")
    print(cm_df)


if __name__ == "__main__":
    main()