from app.api.schemas import ModelResult
from app.models.arabert_model import AraBERTSentimentModel
from app.models.xlm_roberta_model import XLMRobertaSentimentModel
from app.models.llm_model import LLMSentimentModel
from app.models.ensemble import EnsembleModel
from app.models.base_model import SentimentPrediction


class ModelOrchestrator:
    def __init__(self):
        self.arabert = AraBERTSentimentModel()
        self.xlmr = XLMRobertaSentimentModel()
        self.llm = LLMSentimentModel()
        self.ensemble = EnsembleModel()

    def predict(
        self,
        text: str,
        language: str,
        model_name: str = "ensemble",
        context: list[str] | None = None,
    ) -> list[ModelResult]:
        model_name = model_name.lower()

        if model_name == "arabert":
            preds = [self.arabert.predict(text, language, context)]
        elif model_name == "xlmr":
            preds = [self.xlmr.predict(text, language, context)]
        elif model_name == "llm":
            preds = [self.llm.predict(text, language, context)]
        else:
            base_preds = [
                self.arabert.predict(text, language, context),
                self.xlmr.predict(text, language, context),
            ]
            if context:
                base_preds.append(self.llm.predict(text, language, context))
            preds = base_preds + [self.ensemble.combine(base_preds)]

        return [self._to_schema(p) for p in preds]

    def aggregate(self, results: list[ModelResult]) -> dict:
        if not results:
            return {"label": "neutral", "confidence": 0.0}

        ensemble = next((r for r in results if r.model_name == "ensemble"), None)
        selected = ensemble or max(results, key=lambda r: r.score)
        confidence = self._confidence_adjustment(selected)
        return {"label": selected.label, "confidence": confidence}

    def _confidence_adjustment(self, result: ModelResult) -> float:
        probs = sorted(result.probabilities.values(), reverse=True)
        margin = probs[0] - probs[1] if len(probs) > 1 else probs[0]
        adjusted = 0.75 * result.score + 0.25 * margin
        return round(max(0.0, min(1.0, adjusted)), 4)

    @staticmethod
    def _to_schema(pred: SentimentPrediction) -> ModelResult:
        return ModelResult(
            model_name=pred.model_name,
            label=pred.label,
            score=round(pred.score, 4),
            probabilities={k: round(v, 4) for k, v in pred.probabilities.items()},
            explanation=pred.explanation,
        )
