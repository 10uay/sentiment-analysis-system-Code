import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.model_orchestrator import ModelOrchestrator  # noqa: E402
from app.services.preprocessor import TextPreprocessor  # noqa: E402
from app.utils.metrics import compute_metrics  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--text-col", default="text")
    parser.add_argument("--label-col", default="label")
    parser.add_argument("--model", default="ensemble")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    pre = TextPreprocessor()
    orch = ModelOrchestrator()

    preds = []
    for text in df[args.text_col].astype(str):
        clean = pre.clean(text)
        lang = pre.detect_language(clean)
        results = orch.predict(clean, lang, args.model)
        final = orch.aggregate(results)
        preds.append(final["label"])

    metrics = compute_metrics(df[args.label_col].astype(str), preds)
    print(metrics)


if __name__ == "__main__":
    main()
