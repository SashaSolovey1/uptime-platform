from datetime import datetime
from uuid import UUID

from uptime_platform.monitors.entities import (
    Monitor,
    MonitorStatus,
)


class InMemoryMonitorRepository:
    def __init__(self) -> None:
        self._monitors: dict[
            UUID,
            Monitor,
        ] = {}

    async def create(
        self,
        monitor: Monitor,
    ) -> Monitor:
        self._monitors[monitor.id] = monitor

        return monitor

    async def get_all(
        self,
    ) -> list[Monitor]:
        return list(self._monitors.values())

    async def get_by_id(
        self,
        monitor_id: UUID,
    ) -> Monitor | None:
        return self._monitors.get(monitor_id)

    async def get_by_id_for_update(
        self,
        monitor_id: UUID,
    ) -> Monitor | None:
        return await self.get_by_id(monitor_id)

    async def update(
        self,
        monitor: Monitor,
    ) -> Monitor | None:
        if monitor.id not in self._monitors:
            return None

        self._monitors[monitor.id] = monitor

        return monitor

    async def delete(
        self,
        monitor_id: UUID,
    ) -> bool:
        if monitor_id not in self._monitors:
            return False

        del self._monitors[monitor_id]

        return True

    async def get_due(
        self,
        now: datetime,
        limit: int,
    ) -> list[Monitor]:
        monitors = [
            monitor
            for monitor in self._monitors.values()
            if (
                monitor.next_check_at <= now
                and monitor.status is not MonitorStatus.PAUSED
            )
        ]

        monitors.sort(key=lambda monitor: monitor.next_check_at)

        return monitors[:limit]
