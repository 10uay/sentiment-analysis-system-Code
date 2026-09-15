from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


SentimentLabel = Literal["positive", "negative", "neutral", "very_positive", "very_negative"]


class LoginRequest(BaseModel):
    username: str = Field(min_length=2)
    password: str = Field(min_length=2)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    model_name: str = Field(default="ensemble", examples=["arabert", "xlmr", "ensemble", "llm"])
    use_rag: bool = True
    save_history: bool = True


class ModelResult(BaseModel):
    model_name: str
    label: SentimentLabel | str
    score: float = Field(ge=0.0, le=1.0)
    probabilities: dict[str, float]
    explanation: str | None = None


class AnalyzeResponse(BaseModel):
    id: int | None = None
    original_text: str
    cleaned_text: str
    language: str
    final_label: SentimentLabel | str
    confidence: float
    model_results: list[ModelResult]
    rag_context: list[str] = []
    report_summary: str | None = None
    created_at: datetime


class HistoryItem(BaseModel):
    id: int
    text: str
    language: str
    label: str
    confidence: float
    model_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportRequest(BaseModel):
    analysis_ids: list[int] = []
    include_charts: bool = True
    export_format: Literal["pdf", "csv", "json"] = "pdf"


class ModelInfo(BaseModel):
    name: str
    description: str
    labels: list[str]
    available: bool
    type: str


class BatchAnalyzeRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=500)
    model_name: str = "ensemble"
    use_rag: bool = False
    save_history: bool = True


class BatchAnalyzeResponse(BaseModel):
    results: list[AnalyzeResponse]
    stats: dict[str, Any]
