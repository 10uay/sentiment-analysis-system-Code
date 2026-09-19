from collections import defaultdict
from app.models.base_model import SentimentPrediction


class EnsembleModel:
    name = "ensemble"

    # @staticmethod
    # def normalize_label(label: str) -> str:
    #     if label == "very_positive":
    #         return "positive"
    #     if label == "very_negative":
    #         return "negative"
    #     return label

    def combine(self, predictions: list[SentimentPrediction]) -> SentimentPrediction:
        # Accumulators: totals keeps the sum of probabilities per label,
        # counts tracks how many models contributed to each label.
        totals = defaultdict(float)
        counts = defaultdict(int)

        # Aggregate probabilities from every model's prediction.
        for pred in predictions:
            for label, prob in pred.probabilities.items():
                # norm = self.normalize_label(label)
                totals[label] += float(prob)
                counts[label] += 1

        # Compute the average probability per label.
        # max(counts[label], 1) prevents division by zero.
        probs = {}
        for label in ["positive", "negative", "neutral"]:
            probs[label] = totals[label] / max(counts[label], 1)

        # Normalize the averaged probabilities so they sum to 1.0.
        # `or 1.0` guards against an empty/all-zero sum.
        s = sum(probs.values()) or 1.0
        probs = {k: v / s for k, v in probs.items()}

        best = max(probs, key=probs.get)

        return SentimentPrediction(
            model_name=self.name,
            label=best,
            score=probs[best],
            probabilities=probs,
            explanation="Ensemble result from averaging normalized model probabilities.",
        )
