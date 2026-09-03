from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
)

from uptime_platform.notifications.entities import (
    NotificationDestinationType,
)


class NotificationDestinationCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    destination_type: NotificationDestinationType

    enabled: bool = True

    webhook_url: HttpUrl

    webhook_secret: str = Field(
        min_length=16,
        max_length=512,
    )


class NotificationDestinationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    enabled: bool | None = None

    webhook_url: HttpUrl | None = None

    webhook_secret: str | None = Field(
        default=None,
        min_length=16,
        max_length=512,
    )


class NotificationDestinationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    destination_type: NotificationDestinationType
    enabled: bool
    webhook_url: str
    created_at: datetime
