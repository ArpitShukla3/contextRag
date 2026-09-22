"""Centralized, environment-driven application configuration."""

import re
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Contextual RAG API"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api"
    log_level: str = "INFO"

    database_url: str = (
        "postgresql+psycopg://rag:rag@localhost:5432/contextual_rag"
    )

    chunk_size: int = 1000
    chunk_overlap: int = 200
    upload_dir: Path = Path("data/uploads")
    max_upload_size_mb: int = 20

    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-sonnet-4-20250514"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_max_tokens: int = 1024
    llm_temperature: float = 0.3

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    test_database_url: str = (
        "postgresql+psycopg://rag:rag@localhost:5432/contextual_rag_test"
    )

    @field_validator("database_url")
    @classmethod
    def add_driver_if_missing(cls, value: str) -> str:
        """Ensure the psycopg3 driver is present in the database URL.

        Accepts bare ``postgres://`` / ``postgresql://`` URLs (common with
        hosted providers) by injecting the ``+psycopg`` driver token.
        """
        return re.sub(
            r"^(postgresql|postgres)://",
            r"\1+psycopg://",
            value.strip(),
            count=1,
        )

    @model_validator(mode="after")
    def validate_chunking(self) -> "Settings":
        """Validate chunker configuration."""
        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE must be a positive integer.")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError(
                "CHUNK_OVERLAP must be greater than or equal to 0 and "
                "strictly less than CHUNK_SIZE."
            )
        if self.max_upload_size_mb <= 0:
            raise ValueError("MAX_UPLOAD_SIZE_MB must be a positive integer.")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()