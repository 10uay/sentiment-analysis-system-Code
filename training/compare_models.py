import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.model_orchestrator import ModelOrchestrator  # noqa: E402
from app.services.preprocessor import TextPreprocessor  # noqa: E402
from app.utils.metrics import compute_metrics  # noqa: E402


def evaluate(df, text_col, label_col, model_name):
    pre = TextPreprocessor()
    orch = ModelOrchestrator()
    preds = []
    for text in df[text_col].astype(str):
        clean = pre.clean(text)
        lang = pre.detect_language(clean)
        results = orch.predict(clean, lang, model_name)
        preds.append(orch.aggregate(results)["label"])
    m = compute_metrics(df[label_col].astype(str), preds)
    return {"model": model_name, "accuracy": m["accuracy"], "macro_f1": m["macro_f1"], "weighted_f1": m["weighted_f1"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--text-col", default="text")
    parser.add_argument("--label-col", default="label")
    parser.add_argument("--out", default="model_comparison.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    rows = [evaluate(df, args.text_col, args.label_col, m) for m in ["arabert", "xlmr", "ensemble", "llm"]]
    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False)
    print(out)


if __name__ == "__main__":
    main()
