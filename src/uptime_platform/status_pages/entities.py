from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class StatusPageStatus(StrEnum):
    OPERATIONAL = "operational"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class StatusPage:
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    published: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class StatusPageMonitor:
    status_page_id: UUID
    monitor_id: UUID
    position: int
