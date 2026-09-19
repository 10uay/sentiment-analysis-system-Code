from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sentiment Analysis System"
    app_env: str = "dev"
    api_prefix: str = "/api/v1"

    secret_key: str = "change-me"
    access_token_expire_minutes: int = 1440

    database_url: str = "sqlite:///./sentiment.db"
    redis_url: str = "redis://localhost:6379/0"

    # Hugging Face models
    enable_hf_models: bool = True
    enable_arabert_hf: bool = False
    enable_xlmr_hf: bool = True
    arabert_model_name: str = "aubmindlab/bert-base-arabertv02"
    xlmr_model_name: str = "xlm-roberta-base"

    # LLM settings
    enable_llm: bool = False
    llm_provider: str = "mock"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # RAG settings
    enable_rag: bool = True
    vector_index_path: str = "./vector_index.json"

    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, value):
        if isinstance(value, str):
            return [x.strip() for x in value.split(",") if x.strip()]
        return value

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()