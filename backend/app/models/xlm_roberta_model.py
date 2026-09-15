from app.config import get_settings
from app.models.base_model import BaseSentimentModel, SentimentPrediction

settings = get_settings()


class XLMRobertaSentimentModel(BaseSentimentModel):
    name = "xlmr"

    positive_words = {
        "excellent", "great", "good", "happy", "love", "like", "amazing",
        "useful", "positive", "best", "thanks", "nice", "perfect",
        "ممتاز", "رائع", "جيد", "احب", "جميل", "مفيد"
    }

    negative_words = {
        "bad", "terrible", "sad", "hate", "problem", "fail", "weak",
        "negative", "worst", "slow", "expensive", "poor",
        "سيء", "مشكله", "فشل", "ضعيف", "سلبي", "بطيء"
    }

    # Mapping from Hugging Face labels to our 5-class labels.
    # Our trained model was trained with:
    # 0 = very_negative
    # 1 = negative
    # 2 = neutral
    # 3 = positive
    # 4 = very_positive
    label_id_to_5class = {
        "label_0": "very_negative",
        "label_1": "negative",
        "label_2": "neutral",
        "label_3": "positive",
        "label_4": "very_positive",
        "LABEL_0": "very_negative",
        "LABEL_1": "negative",
        "LABEL_2": "neutral",
        "LABEL_3": "positive",
        "LABEL_4": "very_positive",
    }

    def __init__(self):
        self.pipeline = None
        if settings.enable_hf_models:
            self._try_load_pipeline()

    def _try_load_pipeline(self):
        try:
            from transformers import pipeline

            self.pipeline = pipeline(
                "text-classification",
                model=settings.xlmr_model_name,
                tokenizer=settings.xlmr_model_name,
                top_k=None,
            )

            print("XLM-R model loaded successfully from:", settings.xlmr_model_name)

        except Exception as exc:
            print("Failed to load XLM-R model. Falling back to lexicon.")
            print("Reason:", exc)
            self.pipeline = None

    def predict(
        self,
        text: str,
        language: str = "unknown",
        context: list[str] | None = None,
    ) -> SentimentPrediction:

        if self.pipeline:
            return self._predict_hf(text)

        return self._predict_fallback(text)

    def _predict_fallback(self, text: str) -> SentimentPrediction:
        tokens = set(text.lower().split())
        pos = len(tokens & self.positive_words)
        neg = len(tokens & self.negative_words)

        if pos >= 2 and neg == 0:
            probs = {
                "positive": 0.85,
                "neutral": 0.10,
                "negative": 0.05,
            }
        elif pos > neg:
            probs = {
                "positive": 0.70,
                "neutral": 0.20,
                "negative": 0.10,
            }
        elif neg >= 2 and pos == 0:
            probs = {
                "positive": 0.05,
                "neutral": 0.10,
                "negative": 0.85,
            }
        elif neg > pos:
            probs = {
                "positive": 0.10,
                "neutral": 0.20,
                "negative": 0.70,
            }
        else:
            probs = {
                "positive": 0.20,
                "neutral": 0.60,
                "negative": 0.20,
            }

        label = max(probs, key=probs.get)

        return SentimentPrediction(
            model_name=self.name,
            label=label,
            score=probs[label],
            probabilities=probs,
            explanation="XLM-R fallback lexicon was used. Enable HF models for real multilingual inference.",
        )

    def _predict_hf(self, text: str) -> SentimentPrediction:
        output = self.pipeline(text)

        # With top_k=None, Hugging Face usually returns:
        # [[{"label": "...", "score": ...}, ...]]
        # This makes the code robust in case the output shape changes.
        if isinstance(output, list) and len(output) > 0 and isinstance(output[0], list):
            raw_predictions = output[0]
        else:
            raw_predictions = output

        probs_5class = {
            "very_negative": 0.0,
            "negative": 0.0,
            "neutral": 0.0,
            "positive": 0.0,
            "very_positive": 0.0,
        }

        for item in raw_predictions:
            raw_label = str(item["label"])
            score = float(item["score"])

            label_5class = self.label_id_to_5class.get(
                raw_label,
                self.label_id_to_5class.get(raw_label.lower(), raw_label.lower()),
            )

            if label_5class in probs_5class:
                probs_5class[label_5class] = score

        # 5-class best label
        best_5class = max(probs_5class, key=probs_5class.get)

        # Convert 5-class probabilities to 3-class probabilities.
        # Notice:
        # negative = very_negative + negative
        # positive = positive + very_positive
        # neutral remains alone
        probs_3class = {
            "negative": probs_5class["very_negative"] + probs_5class["negative"],
            "neutral": probs_5class["neutral"],
            "positive": probs_5class["positive"] + probs_5class["very_positive"],
        }

        best_3class = max(probs_3class, key=probs_3class.get)

        # ------------------------------------------------------------
        # Neutral correction rule
        # ------------------------------------------------------------
        # If the strongest detailed 5-class label is neutral,
        # keep the final 3-class decision neutral.
        #
        # Why?
        # Because neutral has only one source probability,
        # while negative and positive each combine two classes.
        # Without this rule, neutral can be unfairly overwhelmed.
        # ------------------------------------------------------------
        decision_reason = "standard 5-to-3 probability aggregation"

        if best_5class == "neutral":
            best_3class = "neutral"
            decision_reason = "neutral preserved because detailed 5-class label is neutral"

        # ------------------------------------------------------------
        # Additional uncertainty rule
        # ------------------------------------------------------------
        # If the model is not very confident and neutral is close enough
        # to the winning class, prefer neutral.
        # This helps with factual/informational sentences.
        # ------------------------------------------------------------
        top_score = probs_3class[best_3class]
        neutral_score = probs_3class["neutral"]

        if best_3class != "neutral":
            if top_score < 0.60 and neutral_score >= 0.25 and (top_score - neutral_score) < 0.25:
                best_3class = "neutral"
                decision_reason = "neutral selected due to low confidence and close neutral score"

        explanation = (
            "Prediction generated by Hugging Face XLM-R pipeline. "
            f"Detailed 5-class label: {best_5class}. "
            f"Final 3-class decision rule: {decision_reason}."
        )

        return SentimentPrediction(
            model_name=self.name,
            label=best_3class,
            score=probs_3class[best_3class],
            probabilities=probs_3class,
            explanation=explanation,
        )