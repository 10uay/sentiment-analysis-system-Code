import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

LABELS = {
    "very_negative": 0,
    "negative": 1,
    "neutral": 2,
    "positive": 3,
    "very_positive": 4,
}

ID_TO_LABEL = {v: k for k, v in LABELS.items()}


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)

    accuracy = accuracy_score(labels, preds)

    precision_w, recall_w, f1_w, _ = precision_recall_fscore_support(
        labels,
        preds,
        average="weighted",
        zero_division=0,
    )

    precision_m, recall_m, f1_m, _ = precision_recall_fscore_support(
        labels,
        preds,
        average="macro",
        zero_division=0,
    )

    return {
        "accuracy": accuracy,
        "weighted_precision": precision_w,
        "weighted_recall": recall_w,
        "weighted_f1": f1_w,
        "macro_precision": precision_m,
        "macro_recall": recall_m,
        "macro_f1": f1_m,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-data", required=True)
    parser.add_argument("--val-data", required=True)
    parser.add_argument("--text-col", default="clean_text")
    parser.add_argument("--label-col", default="label")
    parser.add_argument("--model-name", default="xlm-roberta-base")
    parser.add_argument("--output-dir", default="./training/saved_models/xlmr_sentiment_5class_final_v2")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--grad-accum", type=int, default=8)
    args = parser.parse_args()

    try:
        from datasets import Dataset
        from transformers import (
            AutoTokenizer,
            AutoModelForSequenceClassification,
            TrainingArguments,
            Trainer,
        )
    except Exception as exc:
        raise RuntimeError(
            "Install optional dependencies: transformers datasets torch accelerate"
        ) from exc

    train_df = pd.read_csv(args.train_data)
    val_df = pd.read_csv(args.val_data)

    train_df = train_df[train_df[args.label_col].isin(LABELS)].copy()
    val_df = val_df[val_df[args.label_col].isin(LABELS)].copy()

    train_df["labels"] = train_df[args.label_col].map(LABELS)
    val_df["labels"] = val_df[args.label_col].map(LABELS)

    train_df = train_df.dropna(subset=[args.text_col, "labels"]).copy()
    val_df = val_df.dropna(subset=[args.text_col, "labels"]).copy()

    train_df[args.text_col] = train_df[args.text_col].astype(str)
    val_df[args.text_col] = val_df[args.text_col].astype(str)

    print("Train samples:", len(train_df))
    print("Validation samples:", len(val_df))

    print("\nTrain distribution:")
    print(train_df[args.label_col].value_counts())

    print("\nValidation distribution:")
    print(val_df[args.label_col].value_counts())

    print("\nTraining settings:")
    print(f"epochs: {args.epochs}")
    print(f"batch_size: {args.batch_size}")
    print(f"gradient_accumulation_steps: {args.grad_accum}")
    print(f"effective_batch_size: {args.batch_size * args.grad_accum}")
    print(f"learning_rate: {args.learning_rate}")

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    def tokenize(batch):
        return tokenizer(
            batch[args.text_col],
            truncation=True,
            padding="max_length",
            max_length=160,
        )

    train_ds = Dataset.from_pandas(
        train_df[[args.text_col, "labels"]],
        preserve_index=False,
    ).map(tokenize, batched=True)

    val_ds = Dataset.from_pandas(
        val_df[[args.text_col, "labels"]],
        preserve_index=False,
    ).map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=5,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        num_train_epochs=args.epochs,
        weight_decay=0.01,
        warmup_ratio=0.1,
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        logging_steps=100,
        save_total_limit=2,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    print("\nTraining finished.")
    print("Best model saved to:", output_dir)


if __name__ == "__main__":
    main()