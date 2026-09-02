from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class IncidentStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"


@dataclass(frozen=True, slots=True)
class Incident:
    id: UUID
    monitor_id: UUID
    status: IncidentStatus
    started_at: datetime
    resolved_at: datetime | None
