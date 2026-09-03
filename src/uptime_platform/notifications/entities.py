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
