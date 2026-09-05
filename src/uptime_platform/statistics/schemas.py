from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, model_validator


class StatisticsPeriod(StrEnum):
    HOURS_24 = "24h"
    DAYS_7 = "7d"
    DAYS_30 = "30d"


class StatisticsQuery(BaseModel):
    period: StatisticsPeriod | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None

    @model_validator(mode="after")
    def validate_range(self) -> "StatisticsQuery":
        has_starts_at = self.starts_at is not None
        has_ends_at = self.ends_at is not None

        if self.period is not None and (has_starts_at or has_ends_at):
            raise ValueError("period cannot be combined with starts_at or ends_at")

        if has_starts_at != has_ends_at:
            raise ValueError("starts_at and ends_at must be provided together")

        if self.starts_at is None or self.ends_at is None:
            return self

        if self.starts_at.utcoffset() is None or self.ends_at.utcoffset() is None:
            raise ValueError("starts_at and ends_at must include timezone information")

        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")

        if self.ends_at - self.starts_at > timedelta(days=90):
            raise ValueError("statistics range cannot exceed 90 days")

        return self


class MonitorStatisticsResponse(BaseModel):
    monitor_id: UUID

    period: StatisticsPeriod | None
    starts_at: datetime
    ends_at: datetime

    total_checks: int
    successful_checks: int
    failed_checks: int

    uptime_percentage: float | None
    average_response_time_ms: float | None
