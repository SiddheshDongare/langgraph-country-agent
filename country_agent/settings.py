"""Application settings loaded from environment variables."""

from functools import lru_cache

import structlog
from langchain_core.language_models import BaseChatModel
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = structlog.get_logger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COUNTRY_AGENT_", env_file=".env", extra="ignore")

    # LLM configuration
    llm_model: str = "openai/gpt-oss-120b"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.groq.com/openai/v1"

    # REST Countries API (v5 — needs a key from https://restcountries.com; v3.1 is deprecated)
    api_base_url: str = "https://api.restcountries.com/countries/v5"
    api_key: str = ""
    api_timeout_seconds: int = 10

    # CORS — JSON list, e.g. COUNTRY_AGENT_ALLOWED_ORIGINS='["https://foo.app"]' (bare/space-separated fails to parse)
    allowed_origins: list[str] = ["http://localhost:3000"]

    # Observability
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"

    def get_llm(self) -> BaseChatModel:
        """Return a configured ChatOpenAI instance."""
        from langchain_openai import ChatOpenAI

        logger.info("initializing_llm", model=self.llm_model, base_url=self.openai_base_url)
        return ChatOpenAI(
            model=self.llm_model,
            api_key=self.openai_api_key or None,  # type: ignore[arg-type]
            base_url=self.openai_base_url,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
