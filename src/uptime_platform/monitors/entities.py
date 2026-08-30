from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class MonitorStatus(StrEnum):
    PENDING = "pending"
    UP = "up"
    DOWN = "down"
    PAUSED = "paused"


@dataclass(frozen=True, slots=True)
class Monitor:
    id: UUID
    name: str
    url: str
    interval_seconds: int
    timeout_seconds: int
    status: MonitorStatus
    created_at: datetime
