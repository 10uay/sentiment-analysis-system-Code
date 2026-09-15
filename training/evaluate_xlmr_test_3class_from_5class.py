from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)


INPUT_PATH = Path("training/outputs/xlmr_test_final_v3/xlmr_test_results.csv")
OUTPUT_DIR = Path("training/outputs/xlmr_test_final_v3_3class")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LABELS_3 = ["negative", "neutral", "positive"]


def to_3class(label):
    label = str(label).strip()

    if label in ["very_negative", "negative"]:
        return "negative"

    if label == "neutral":
        return "neutral"

    if label in ["positive", "very_positive"]:
        return "positive"

    return "unknown"


def main():
    df = pd.read_csv(INPUT_PATH)

    df["true_3class"] = df["true_label"].apply(to_3class)
    df["predicted_3class"] = df["predicted_label"].apply(to_3class)
    df["is_correct_3class"] = df["true_3class"] == df["predicted_3class"]

    y_true = df["true_3class"].tolist()
    y_pred = df["predicted_3class"].tolist()

    accuracy = accuracy_score(y_true, y_pred)

    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=LABELS_3,
        average="weighted",
        zero_division=0,
    )

    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=LABELS_3,
        average="macro",
        zero_division=0,
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS_3,
        zero_division=0,
    )

    cm = confusion_matrix(y_true, y_pred, labels=LABELS_3)
    cm_df = pd.DataFrame(cm, index=LABELS_3, columns=LABELS_3)

    df.to_csv(OUTPUT_DIR / "xlmr_test_results_3class.csv", index=False, encoding="utf-8-sig")
    cm_df.to_csv(OUTPUT_DIR / "xlmr_test_confusion_matrix_3class.csv", encoding="utf-8-sig")

    with open(OUTPUT_DIR / "xlmr_test_classification_report_3class.txt", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n3-Class Evaluation from 5-Class Model")
    print("-----------------------------------")
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