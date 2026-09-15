import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)
from transformers import AutoTokenizer, AutoModelForSequenceClassification


LABELS = {
    "very_negative": 0,
    "negative": 1,
    "neutral": 2,
    "positive": 3,
    "very_positive": 4,
}

ID_TO_LABEL = {v: k for k, v in LABELS.items()}


def predict_batch(texts, tokenizer, model, device, batch_size):
    predictions = []
    confidences = []

    model.eval()

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]

        inputs = tokenizer(
            batch_texts,
            truncation=True,
            padding=True,
            max_length=160,
            return_tensors="pt",
        )

        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            conf, pred = torch.max(probs, dim=-1)

        predictions.extend(pred.cpu().tolist())
        confidences.extend(conf.cpu().tolist())

    return predictions, confidences


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test-data",
        default="data_pipeline/processed/splits_5class/test.csv"
    )
    parser.add_argument(
        "--model-dir",
        default="training/saved_models/xlmr_sentiment_5class_final"
    )
    parser.add_argument("--text-col", default="clean_text")
    parser.add_argument("--label-col", default="label")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--out-dir",
        default="training/outputs/xlmr_test_final"
    )

    args = parser.parse_args()

    test_path = Path(args.test_data)
    model_dir = Path(args.model_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading test data:")
    print(test_path)

    df = pd.read_csv(test_path)

    df = df[df[args.label_col].isin(LABELS)].copy()
    df = df.dropna(subset=[args.text_col, args.label_col]).copy()

    df["true_id"] = df[args.label_col].map(LABELS)
    df[args.text_col] = df[args.text_col].astype(str)

    print(f"Test samples: {len(df)}")
    print("\nTest distribution:")
    print(df[args.label_col].value_counts())

    print("\nLoading trained model:")
    print(model_dir)

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("\nUsing device:", device)

    model.to(device)

    texts = df[args.text_col].tolist()
    y_true_ids = df["true_id"].tolist()

    y_pred_ids, confidences = predict_batch(
        texts=texts,
        tokenizer=tokenizer,
        model=model,
        device=device,
        batch_size=args.batch_size,
    )

    y_true = [ID_TO_LABEL[i] for i in y_true_ids]
    y_pred = [ID_TO_LABEL[i] for i in y_pred_ids]

    accuracy = accuracy_score(y_true, y_pred)

    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(LABELS.keys()),
        average="weighted",
        zero_division=0,
    )

    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(LABELS.keys()),
        average="macro",
        zero_division=0,
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=list(LABELS.keys()),
        zero_division=0,
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=list(LABELS.keys()),
    )

    results_df = df.copy()
    results_df["true_label"] = y_true
    results_df["predicted_label"] = y_pred
    results_df["confidence"] = confidences
    results_df["is_correct"] = results_df["true_label"] == results_df["predicted_label"]

    results_path = out_dir / "xlmr_test_results.csv"
    metrics_path = out_dir / "xlmr_test_metrics.json"
    report_path = out_dir / "xlmr_test_classification_report.txt"
    cm_path = out_dir / "xlmr_test_confusion_matrix.csv"

    results_df.to_csv(results_path, index=False, encoding="utf-8-sig")

    cm_df = pd.DataFrame(
        cm,
        index=list(LABELS.keys()),
        columns=list(LABELS.keys()),
    )
    cm_df.to_csv(cm_path, encoding="utf-8-sig")

    metrics = {
        "model": "xlmr_sentiment_5class_final",
        "evaluation_split": "test",
        "total_test_samples": len(df),
        "accuracy": accuracy,
        "weighted_precision": weighted_precision,
        "weighted_recall": weighted_recall,
        "weighted_f1": weighted_f1,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "labels": list(LABELS.keys()),
        "confusion_matrix": cm.tolist(),
    }

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\nEvaluation finished.")
    print(f"Results saved to: {results_path}")
    print(f"Metrics saved to: {metrics_path}")
    print(f"Report saved to: {report_path}")
    print(f"Confusion matrix saved to: {cm_path}")

    print("\nMain Metrics:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Weighted Precision: {weighted_precision:.4f}")
    print(f"Weighted Recall: {weighted_recall:.4f}")
    print(f"Weighted F1-score: {weighted_f1:.4f}")
    print(f"Macro F1-score: {macro_f1:.4f}")

    print("\nClassification Report:")
    print(report)

    print("\nConfusion Matrix:")
    print(cm_df)


if __name__ == "__main__":
    main()