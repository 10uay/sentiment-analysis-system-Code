from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "training" / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def save_bar_chart(df, x_col, y_col, title, ylabel, filename):
    plt.figure(figsize=(8, 5))
    plt.bar(df[x_col].astype(str), df[y_col])
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    out_path = FIGURES_DIR / filename
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_rag_comparison():
    path = OUTPUT_DIR / "api_rag_comparison_summary.csv"

    if not path.exists():
        print(f"Skipped RAG comparison. Missing file: {path}")
        return

    df = pd.read_csv(path)

    # نحذف سطر الفرق ونبقي فقط التجربتين
    df_exp = df[df["experiment"].str.contains("Difference") == False].copy()

    save_bar_chart(
        df_exp,
        x_col="experiment",
        y_col="accuracy",
        title="Accuracy Comparison: With RAG vs Without RAG",
        ylabel="Accuracy",
        filename="rag_accuracy_comparison.png",
    )

    save_bar_chart(
        df_exp,
        x_col="experiment",
        y_col="weighted_f1",
        title="Weighted F1-score Comparison: With RAG vs Without RAG",
        ylabel="Weighted F1-score",
        filename="rag_weighted_f1_comparison.png",
    )

    save_bar_chart(
        df_exp,
        x_col="experiment",
        y_col="average_runtime_per_sample_seconds",
        title="Average Runtime per Sample",
        ylabel="Seconds",
        filename="rag_runtime_comparison.png",
    )


def plot_model_comparison():
    path = OUTPUT_DIR / "model_comparison.csv"

    if not path.exists():
        print(f"Skipped model comparison. Missing file: {path}")
        return

    df = pd.read_csv(path)

    save_bar_chart(
        df,
        x_col="model",
        y_col="accuracy",
        title="Model Accuracy Comparison",
        ylabel="Accuracy",
        filename="model_accuracy_comparison.png",
    )

    save_bar_chart(
        df,
        x_col="model",
        y_col="macro_f1",
        title="Model Macro F1-score Comparison",
        ylabel="Macro F1-score",
        filename="model_macro_f1_comparison.png",
    )

    save_bar_chart(
        df,
        x_col="model",
        y_col="weighted_f1",
        title="Model Weighted F1-score Comparison",
        ylabel="Weighted F1-score",
        filename="model_weighted_f1_comparison.png",
    )


def plot_confusion_matrix(csv_name, title, filename):
    path = OUTPUT_DIR / csv_name

    if not path.exists():
        print(f"Skipped confusion matrix. Missing file: {path}")
        return

    df = pd.read_csv(path, index_col=0)

    plt.figure(figsize=(6, 5))
    plt.imshow(df.values)
    plt.title(title)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")

    plt.xticks(range(len(df.columns)), df.columns)
    plt.yticks(range(len(df.index)), df.index)

    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            plt.text(j, i, str(df.values[i, j]), ha="center", va="center")

    plt.tight_layout()
    out_path = FIGURES_DIR / filename
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def main():
    plot_rag_comparison()
    plot_model_comparison()

    plot_confusion_matrix(
        csv_name="api_with_rag_confusion_matrix.csv",
        title="Confusion Matrix - API With RAG",
        filename="confusion_matrix_with_rag.png",
    )

    plot_confusion_matrix(
        csv_name="api_without_rag_confusion_matrix.csv",
        title="Confusion Matrix - API Without RAG",
        filename="confusion_matrix_without_rag.png",
    )

    print("\nAll available figures were generated successfully.")


if __name__ == "__main__":
    main()