"""OpsMesh Configuration Module."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Aplicação ---
    APP_ENV: Literal["development", "staging", "production", "test"] = "development"
    LOG_LEVEL: str = "INFO"
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    WEBHOOK_SECRET: str = "opsmesh-webhook-secret-key-change-in-prod"

    # --- Modelos de Linguagem ---
    DEFAULT_LLM_PROVIDER: Literal["openai", "deepseek", "gemini"] = "deepseek"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL_NAME: str = "deepseek-v4.1-flash"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-1.5-flash"

    # --- CORS Security ---
    CORS_ORIGINS: str = "*"

    # --- Persistência de Checkpoints (PostgreSQL Serverless) ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/opsmesh"

    # --- Qdrant Vector Store ---
    QDRANT_LOCATION: str = ":memory:"
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""

    # --- FinOps & Blindagem Anti-Abuso ---
    DEMO_MODE: bool = False
    FINOPS_DAILY_BUDGET_USD: float = 1.00
    FINOPS_DAILY_TOKEN_LIMIT: int = 150_000
    FINOPS_MAX_TOKENS_PER_INCIDENT: int = 12_000
    FINOPS_MAX_SUPERVISOR_ITERATIONS: int = 4
    RATE_LIMIT_PER_MINUTE: int = 5

    # --- Observabilidade ---
    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "opsmesh"

    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"


settings = Settings()
