from app.config import get_settings
from app.models.base_model import BaseSentimentModel, SentimentPrediction

settings = get_settings()


class LLMSentimentModel(BaseSentimentModel):
    name = "llm"

    def predict(self, text: str, language: str = "unknown", context: list[str] | None = None) -> SentimentPrediction:
        # النسخة التعليمية لا ترسل النص إلى مزود خارجي افتراضياً.
        # يمكن لاحقاً ربط OpenAI/Claude هنا عند تفعيل ENABLE_LLM وتوفير المفاتيح.
        context_text = "\n".join(context or [])
        explanation = (
            "LLM fallback explanation: the model checks polarity words, tone, and retrieved context. "
            f"Retrieved context length={len(context_text)} chars."
        )

        lower = text.lower()
        negative_markers = ["سيء", "مشكله", "مشكلة", "bad", "terrible", "hate", "worst"]
        positive_markers = ["رائع", "ممتاز", "جيد", "great", "excellent", "love", "best"]

        pos = sum(1 for w in positive_markers if w in lower)
        neg = sum(1 for w in negative_markers if w in lower)

        if pos > neg:
            probs = {"positive": 0.70, "negative": 0.10, "neutral": 0.20}
        elif neg > pos:
            probs = {"positive": 0.10, "negative": 0.70, "neutral": 0.20}
        else:
            probs = {"positive": 0.25, "negative": 0.20, "neutral": 0.55}

        label = max(probs, key=probs.get)
        return SentimentPrediction(
            model_name=self.name,
            label=label,
            score=probs[label],
            probabilities=probs,
            explanation=explanation,
        )
