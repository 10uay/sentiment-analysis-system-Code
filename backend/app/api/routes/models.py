from fastapi import APIRouter

from app.api.schemas import ModelInfo

router = APIRouter()


@router.get("/models", response_model=list[ModelInfo])
def list_models():
    return [
        ModelInfo(
            name="arabert",
            description="Arabic sentiment model. Uses AraBERT if enabled, otherwise Arabic lexicon fallback.",
            labels=["positive", "negative", "neutral"],
            available=True,
            type="transformer/fallback",
        ),
        ModelInfo(
            name="xlmr",
            description="Multilingual Arabic/English model. Uses XLM-R if enabled, otherwise multilingual fallback.",
            labels=["very_negative", "negative", "neutral", "positive", "very_positive"],
            available=True,
            type="transformer/fallback",
        ),
        ModelInfo(
            name="ensemble",
            description="Combines available models using probability averaging and confidence logic.",
            labels=["positive", "negative", "neutral"],
            available=True,
            type="ensemble",
        ),
        ModelInfo(
            name="llm",
            description="LLM/RAG-augmented explanation model. Uses API if enabled, otherwise mock explanation.",
            labels=["positive", "negative", "neutral"],
            available=True,
            type="llm/fallback",
        ),
    ]
