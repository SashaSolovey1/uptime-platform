from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CheckResult:
    success: bool
    response_time_ms: float
    status_code: int | None
    error: str | None
    details: dict[str, object] | None = None


@dataclass(frozen=True, slots=True)
class Check:
    id: int
    monitor_id: UUID
    success: bool
    response_time_ms: float
    status_code: int | None
    error: str | None
    checked_at: datetime
    details: dict[str, object] | None = None
