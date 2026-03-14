"""Application settings loaded from environment variables."""

from functools import lru_cache

import structlog
from langchain_core.language_models import BaseChatModel
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = structlog.get_logger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COUNTRY_AGENT_", env_file=".env", extra="ignore")

    # LLM configuration
    llm_provider: str = "openai"  # "openai" or "anthropic"
    llm_model: str = ""  # auto-selected if empty
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # REST Countries API
    api_base_url: str = "https://restcountries.com/v3.1"
    api_timeout_seconds: int = 10

    # Observability
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"

    @property
    def resolved_llm_model(self) -> str:
        if self.llm_model:
            return self.llm_model
        return "gpt-4o-mini" if self.llm_provider == "openai" else "claude-sonnet-4-6"

    def get_llm(self) -> BaseChatModel:
        """Return a configured ChatModel based on provider settings."""
        if self.llm_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            logger.info("initializing_llm", provider="anthropic", model=self.resolved_llm_model)
            return ChatAnthropic(
                model=self.resolved_llm_model,
                api_key=self.anthropic_api_key or None,  # type: ignore[arg-type]
            )

        from langchain_openai import ChatOpenAI

        logger.info("initializing_llm", provider="openai", model=self.resolved_llm_model)
        return ChatOpenAI(
            model=self.resolved_llm_model,
            api_key=self.openai_api_key or None,  # type: ignore[arg-type]
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
