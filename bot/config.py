"""Configuration module for the Telegram bot."""

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env.bot.secret in parent directory (repo root) or current directory (Docker)
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR.parent / ".env.bot.secret"

# Fallback to current directory for Docker deployment
if not ENV_FILE.exists():
    ENV_FILE = Path("/app/.env.bot.secret")
    if not ENV_FILE.exists():
        ENV_FILE = BASE_DIR / ".env.bot.secret"

ENV_FILE = str(ENV_FILE)


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str | None = None

    # LMS API
    lms_api_base_url: str = "http://localhost:8000"
    lms_api_key: str = ""

    # LLM API (for intent routing)
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"

    # Test mode flag (set via CLI, not env)
    test_mode: bool = False


@lru_cache
def get_settings() -> BotSettings:
    """Get cached bot settings instance."""
    return BotSettings()


def load_config(test_mode: bool = False) -> BotSettings:
    """Load configuration with optional test mode."""
    settings = get_settings()
    settings.test_mode = test_mode
    return settings


def validate_config(settings: BotSettings, test_mode: bool = False) -> list[str]:
    """Validate configuration and return list of errors."""
    errors = []

    if not test_mode and not settings.bot_token:
        errors.append("BOT_TOKEN is required for Telegram mode")

    # LMS_API_KEY only required in Telegram mode (test mode uses placeholders)
    if not test_mode and not settings.lms_api_key:
        errors.append("LMS_API_KEY is required")

    return errors
