from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiKeySettings(BaseSettings):
    api_key_hash_secret: SecretStr = Field(
        min_length=32,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_api_key_settings() -> ApiKeySettings:
    # noinspection PyArgumentList
    return ApiKeySettings()
