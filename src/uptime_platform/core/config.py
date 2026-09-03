from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    notification_channel: Literal[
        "console",
        "webhook",
    ] = "console"

    webhook_url: str | None = None
    webhook_secret: SecretStr | None = None

    webhook_timeout_seconds: float = Field(
        default=5.0,
        gt=0,
        le=60,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
