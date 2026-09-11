from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class AuthSettings(BaseSettings):
    jwt_secret: SecretStr = Field(
        min_length=32,
    )

    jwt_algorithm: Literal["HS256"] = "HS256"

    jwt_access_token_ttl_minutes: int = Field(
        default=60,
        ge=1,
        le=1440,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()
