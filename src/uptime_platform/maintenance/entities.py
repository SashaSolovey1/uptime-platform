from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class MaintenanceWindow:
    id: UUID
    monitor_id: UUID
    starts_at: datetime
    ends_at: datetime
    reason: str | None
    created_at: datetime

    def is_active(
        self,
        now: datetime,
    ) -> bool:
        return self.starts_at <= now < self.ends_at
