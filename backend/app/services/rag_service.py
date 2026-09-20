from app.config import get_settings
from app.services.embedding_service import EmbeddingService

settings = get_settings()


class RAGService:
    def __init__(self):
        self.embeddings = EmbeddingService()

    def _normalize_label_to_3class(self, label: str | None) -> str:
        """
        Convert any dataset/model label into 3-class label:
        positive / negative / neutral
        """
        if label is None:
            return "unknown"

        label = str(label).strip().lower()

        if label in ["very_positive", "positive", "label_3", "label_4"]:
            return "positive"

        if label in ["very_negative", "negative", "label_0", "label_1"]:
            return "negative"

        if label in ["neutral", "label_2"]:
            return "neutral"

        return "unknown"

    def _get_item_label(self, item: dict) -> str:
        """
        Extract label from vector index item.
        The index usually stores label inside item["metadata"]["label"].
        """
        metadata = item.get("metadata", {})

        label = (
            metadata.get("label")
            or metadata.get("sentiment")
            or item.get("label")
            or item.get("sentiment")
        )

        return self._normalize_label_to_3class(label)

    def retrieve(
        self,
        query: str,
        language: str = "unknown",
        top_k: int = 3,
        target_label: str | None = None,
    ) -> list[str]:
        # Retrieve similar texts from the vector index.
        # If target_label is provided, the method prefers examples
        # that have the same sentiment class as the model prediction.

        if not settings.enable_rag:
            return []

        index = self.embeddings.load_index()
        if not index:
            return self._default_context(query, language)

        target_label_3class = self._normalize_label_to_3class(target_label)

        q = self.embeddings.embed(query)

        scored = []

        for item in index:
            score = self.embeddings.cosine(q, item.get("embedding", []))

            if score <= 0.05:
                continue

            item_label_3class = self._get_item_label(item)

            scored.append(
                {
                    "score": score,
                    "text": item.get("text", ""),
                    "label": item_label_3class,
                    "item": item,
                }
            )

        scored.sort(reverse=True, key=lambda x: x["score"])

        # First: try to return examples matching the final predicted label
        if target_label_3class in ["positive", "negative", "neutral"]:
            filtered = [
                x for x in scored
                if x["label"] == target_label_3class and x["text"].strip()
            ]

            if len(filtered) >= top_k:
                return [x["text"] for x in filtered[:top_k]]

            # If we found some matching examples, return only them.
            # Better to show fewer relevant examples than many contradictory examples.
            if len(filtered) > 0:
                return [x["text"] for x in filtered[:top_k]]

        # If no target_label was provided, or no labeled examples were found,
        # return the most similar examples as before.
        return [x["text"] for x in scored[:top_k] if x["text"].strip()]

    def build_prompt(self, text: str, context: list[str]) -> str:
        return (
            "Analyze the sentiment of the following text using the retrieved context.\n\n"
            f"Text:\n{text}\n\n"
            f"Context:\n{chr(10).join(context)}\n\n"
            "Return JSON with label, confidence, and explanation."
        )

    def _default_context(self, query: str, language: str) -> list[str]:
        if language == "ar":
            return [
                "تحليل المشاعر يصنف النص عادة إلى إيجابي أو سلبي أو محايد.",
                "في النصوص العربية يجب الانتباه إلى اللهجات، النفي، والسياق العام للجملة.",
            ]

        return [
            "Sentiment analysis usually classifies text as positive, negative, or neutral.",
            "For multilingual text, language detection and normalization improve model reliability.",
        ]