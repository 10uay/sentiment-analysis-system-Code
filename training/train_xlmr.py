import argparse
import pandas as pd
from sklearn.model_selection import train_test_split

LABELS = {"very_negative": 0, "negative": 1, "neutral": 2, "positive": 3, "very_positive": 4}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--text-col", default="clean_text")
    parser.add_argument("--label-col", default="label")
    parser.add_argument("--model-name", default="xlm-roberta-base")
    parser.add_argument("--output-dir", default="./xlmr_sentiment")
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()

    try:
        from datasets import Dataset
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
    except Exception as exc:
        raise RuntimeError("Install optional dependencies: transformers datasets torch accelerate") from exc

    df = pd.read_csv(args.data)
    df = df[df[args.label_col].isin(LABELS)].copy()
    df["labels"] = df[args.label_col].map(LABELS)

    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["labels"])
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    def tokenize(batch):
        return tokenizer(batch[args.text_col], truncation=True, padding="max_length", max_length=160)

    train_ds = Dataset.from_pandas(train_df[[args.text_col, "labels"]]).map(tokenize, batched=True)
    val_ds = Dataset.from_pandas(val_df[[args.text_col, "labels"]]).map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(args.model_name, num_labels=5)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        num_train_epochs=args.epochs,
        weight_decay=0.01,
        load_best_model_at_end=True,
        logging_steps=50,
    )

    trainer = Trainer(model=model, args=training_args, train_dataset=train_ds, eval_dataset=val_ds)
    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
