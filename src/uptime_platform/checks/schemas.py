from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monitor_id: UUID
    success: bool
    response_time_ms: float
    status_code: int | None
    error: str | None
    details: dict[str, object] | None = None
    checked_at: datetime
