# مثال بسيط لتسجيل التجارب في MLflow.
# يتطلب:
# pip install mlflow
import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics-json", required=True)
    parser.add_argument("--run-name", default="sentiment-experiment")
    args = parser.parse_args()

    import mlflow

    with open(args.metrics_json, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with mlflow.start_run(run_name=args.run_name):
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(key, value)
        mlflow.log_dict(metrics, "metrics.json")

    print("Logged metrics to MLflow")


if __name__ == "__main__":
    main()
