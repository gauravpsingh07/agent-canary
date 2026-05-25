from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Agent Canary"
    app_env: str = "local"
    app_debug: bool = False

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    jwt_secret: str = "replace-with-a-long-random-development-secret"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/agent_canary"

    llm_provider: str = "mock"
    mock_llm_model: str = "mock-agent-canary-v1"
    gemini_api_key: str = ""
    gemini_model: str = ""
    groq_api_key: str = ""
    groq_model: str = ""
    openai_api_key: str = ""
    openai_model: str = ""
    llm_timeout_seconds: float = 30.0

    embedding_provider: str = "mock"
    mock_embedding_model: str = "mock-embedding-v1"
    gemini_embedding_model: str = "text-embedding-004"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 768
    embedding_timeout_seconds: float = 30.0
    rag_chunk_max_chars: int = 1000
    rag_chunk_overlap_chars: int = 120
    retrieval_default_min_score: float = 0.25
    retrieval_default_max_results: int = 5

    redis_url: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return value
        raise TypeError("CORS_ORIGINS must be a comma-separated string or list")


@lru_cache
def get_settings() -> Settings:
    return Settings()
