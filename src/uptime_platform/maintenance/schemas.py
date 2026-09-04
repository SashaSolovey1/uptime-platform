from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class MaintenanceWindowCreate(BaseModel):
    monitor_id: UUID

    starts_at: datetime
    ends_at: datetime

    reason: str | None = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def validate_time_range(
        self,
    ) -> "MaintenanceWindowCreate":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")

        return self


class MaintenanceWindowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    monitor_id: UUID

    starts_at: datetime
    ends_at: datetime

    reason: str | None

    created_at: datetime
