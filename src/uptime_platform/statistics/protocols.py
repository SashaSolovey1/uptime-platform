from datetime import datetime
from typing import Protocol
from uuid import UUID

from uptime_platform.statistics.entities import (
    MonitorStatistics,
)


class StatisticsRepositoryProtocol(Protocol):
    async def get_monitor_statistics(
        self,
        monitor_id: UUID,
        starts_at: datetime,
        ends_at: datetime,
    ) -> MonitorStatistics: ...
