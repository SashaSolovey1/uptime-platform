from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from uptime_platform.notifications.entities import (
    NotificationDestinationType,
)


class WebhookDestinationConfigCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    url: HttpUrl

    secret: str = Field(
        min_length=16,
        max_length=512,
    )


class TelegramDestinationConfigCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    bot_token: str = Field(
        min_length=1,
        max_length=512,
    )

    chat_id: str = Field(
        min_length=1,
        max_length=100,
    )


class NotificationDestinationCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    destination_type: NotificationDestinationType

    enabled: bool = True

    config: WebhookDestinationConfigCreate | TelegramDestinationConfigCreate

    @model_validator(mode="after")
    def validate_config(
        self,
    ) -> "NotificationDestinationCreate":
        if (
            self.destination_type is NotificationDestinationType.WEBHOOK
            and not isinstance(
                self.config,
                WebhookDestinationConfigCreate,
            )
        ):
            raise ValueError("Webhook destination requires webhook configuration")

        if (
            self.destination_type is NotificationDestinationType.TELEGRAM
            and not isinstance(
                self.config,
                TelegramDestinationConfigCreate,
            )
        ):
            raise ValueError("Telegram destination requires Telegram configuration")

        return self


class WebhookDestinationConfigUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    url: HttpUrl | None = None

    secret: str | None = Field(
        default=None,
        min_length=16,
        max_length=512,
    )


class TelegramDestinationConfigUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    bot_token: str | None = Field(
        default=None,
        min_length=1,
        max_length=512,
    )

    chat_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class NotificationDestinationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    enabled: bool | None = None

    config: WebhookDestinationConfigUpdate | TelegramDestinationConfigUpdate | None = (
        None
    )


class WebhookDestinationConfigResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    url: str


class TelegramDestinationConfigResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    chat_id: str


class NotificationDestinationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    destination_type: NotificationDestinationType
    enabled: bool

    config: WebhookDestinationConfigResponse | TelegramDestinationConfigResponse

    created_at: datetime
