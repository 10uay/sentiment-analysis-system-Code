from collections import defaultdict
from app.models.base_model import SentimentPrediction


class EnsembleModel:
    name = "ensemble"

    @staticmethod
    def normalize_label(label: str) -> str:
        if label == "very_positive":
            return "positive"
        if label == "very_negative":
            return "negative"
        return label

    def combine(self, predictions: list[SentimentPrediction]) -> SentimentPrediction:
        totals = defaultdict(float)
        counts = defaultdict(int)

        for pred in predictions:
            for label, prob in pred.probabilities.items():
                norm = self.normalize_label(label)
                totals[norm] += float(prob)
                counts[norm] += 1

        probs = {}
        for label in ["positive", "negative", "neutral"]:
            probs[label] = totals[label] / max(counts[label], 1)

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
