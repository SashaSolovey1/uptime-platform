from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    model_validator,
)

from uptime_platform.notifications.entities import (
    EmailSecurity,
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


class EmailDestinationConfigCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    host: str = Field(
        min_length=1,
        max_length=255,
    )

    port: int = Field(
        ge=1,
        le=65535,
    )

    username: str | None = Field(
        default=None,
        max_length=255,
    )

    password: str | None = Field(
        default=None,
        max_length=512,
    )

    from_email: EmailStr
    to_email: EmailStr
    security: EmailSecurity


class NotificationDestinationCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    destination_type: NotificationDestinationType

    enabled: bool = True

    config: (
        WebhookDestinationConfigCreate
        | TelegramDestinationConfigCreate
        | EmailDestinationConfigCreate
    )

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

        if (
            self.destination_type is NotificationDestinationType.EMAIL
            and not isinstance(
                self.config,
                EmailDestinationConfigCreate,
            )
        ):
            raise ValueError("Email destination requires email configuration")

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


class EmailDestinationConfigUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    host: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
    )

    username: str | None = Field(
        default=None,
        max_length=255,
    )

    password: str | None = Field(
        default=None,
        max_length=512,
    )

    from_email: EmailStr | None = None
    to_email: EmailStr | None = None
    security: EmailSecurity | None = None


class NotificationDestinationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    enabled: bool | None = None

    config: (
        WebhookDestinationConfigUpdate
        | TelegramDestinationConfigUpdate
        | EmailDestinationConfigUpdate
        | None
    ) = None


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


class EmailDestinationConfigResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    host: str
    port: int
    username: str | None
    from_email: str
    to_email: str
    security: EmailSecurity


class NotificationDestinationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    destination_type: NotificationDestinationType
    enabled: bool

    config: (
        WebhookDestinationConfigResponse
        | TelegramDestinationConfigResponse
        | EmailDestinationConfigResponse
    )

    created_at: datetime
