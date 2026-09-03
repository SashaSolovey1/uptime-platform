from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class NotificationDestinationType(StrEnum):
    WEBHOOK = "webhook"


@dataclass(frozen=True, slots=True)
class NotificationDestination:
    id: UUID
    name: str
    destination_type: NotificationDestinationType
    enabled: bool
    webhook_url: str
    webhook_secret: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class NotificationDelivery:
    id: UUID
    event_id: UUID
    destination_id: UUID
    created_at: datetime
    processed_at: datetime | None
    attempts: int
    last_error: str | None
    next_attempt_at: datetime
    locked_until: datetime | None
