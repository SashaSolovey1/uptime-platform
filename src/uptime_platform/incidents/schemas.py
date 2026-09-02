from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from uptime_platform.incidents.entities import (
    IncidentStatus,
)


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    monitor_id: UUID
    status: IncidentStatus
    started_at: datetime
    resolved_at: datetime | None
