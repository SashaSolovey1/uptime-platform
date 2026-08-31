from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from uptime_platform.monitors.entities import MonitorStatus


class MonitorCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    url: HttpUrl

    interval_seconds: int = Field(
        default=60,
        ge=10,
        le=3600,
    )

    timeout_seconds: int = Field(
        default=5,
        ge=1,
        le=60,
    )

    failure_threshold: int = Field(
        default=3,
        ge=1,
        le=10,
    )

    recovery_threshold: int = Field(
        default=2,
        ge=1,
        le=10,
    )


class MonitorResponse(MonitorCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: MonitorStatus
    created_at: datetime
    consecutive_failures: int
    consecutive_successes: int
    next_check_at: datetime


failure_threshold: int | None = Field(
    default=None,
    ge=1,
    le=10,
)

recovery_threshold: int | None = Field(
    default=None,
    ge=1,
    le=10,
)


class MonitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    url: HttpUrl | None = None
    interval_seconds: int | None = Field(default=None, ge=10, le=3600)
    timeout_seconds: int | None = Field(default=None, ge=1, le=60)
