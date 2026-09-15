import json
from pathlib import Path

import pandas as pd
import torch
from sklearn.model_selection import train_test_split
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


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data_pipeline" / "processed" / "ar_en_5class_clean.csv"
MODEL_DIR = PROJECT_ROOT / "training" / "saved_models" / "xlmr_sentiment_5class"
OUTPUT_DIR = PROJECT_ROOT / "training" / "outputs" / "trained_xlmr"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def predict_batch(texts, tokenizer, model, device, batch_size=16):
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
    print("Loading dataset:")
    print(DATA_PATH)

    df = pd.read_csv(DATA_PATH)

    df = df[df["label"].isin(LABELS)].copy()
    df["labels"] = df["label"].map(LABELS)

    # إعادة نفس تقسيم train_xlmr.py تقريبًا
    train_df, val_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["labels"],
    )

    print(f"Total samples: {len(df)}")
    print(f"Validation samples: {len(val_df)}")

    print("\nValidation distribution:")
    print(val_df["label"].value_counts())

    print("\nLoading trained model:")
    print(MODEL_DIR)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nUsing device: {device}")

    model.to(device)

    texts = val_df["clean_text"].astype(str).tolist()
    y_true_ids = val_df["labels"].tolist()

    y_pred_ids, confidences = predict_batch(
        texts=texts,
        tokenizer=tokenizer,
        model=model,
        device=device,
        batch_size=16,
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

    results_df = val_df.copy()
    results_df["true_label"] = y_true
    results_df["predicted_label"] = y_pred
    results_df["confidence"] = confidences
    results_df["is_correct"] = results_df["true_label"] == results_df["predicted_label"]

    results_path = OUTPUT_DIR / "xlmr_5class_validation_results.csv"
    metrics_path = OUTPUT_DIR / "xlmr_5class_validation_metrics.json"
    report_path = OUTPUT_DIR / "xlmr_5class_classification_report.txt"
    cm_path = OUTPUT_DIR / "xlmr_5class_confusion_matrix.csv"

    results_df.to_csv(results_path, index=False, encoding="utf-8-sig")

    cm_df = pd.DataFrame(
        cm,
        index=list(LABELS.keys()),
        columns=list(LABELS.keys()),
    )
    cm_df.to_csv(cm_path, encoding="utf-8-sig")

    metrics = {
        "model": "xlmr_sentiment_5class",
        "evaluation_split": "validation",
        "total_validation_samples": len(val_df),
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