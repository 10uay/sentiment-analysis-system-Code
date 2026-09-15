from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class SentimentPrediction(BaseModel):
    model_name: str
    label: str
    score: float = Field(ge=0.0, le=1.0)
    probabilities: dict[str, float]
    explanation: str | None = None


class BaseSentimentModel(ABC):
    name: str

    @abstractmethod
    def predict(self, text: str, language: str = "unknown", context: list[str] | None = None) -> SentimentPrediction:
        raise NotImplementedError
