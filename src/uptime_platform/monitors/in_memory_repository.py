from uuid import UUID

from uptime_platform.monitors.entities import Monitor


class InMemoryMonitorRepository:
    def __init__(self) -> None:
        self._monitors: dict[UUID, Monitor] = {}

    async def create(
        self,
        monitor: Monitor,
    ) -> Monitor:
        self._monitors[monitor.id] = monitor
        return monitor

    async def get_all(self) -> list[Monitor]:
        return list(self._monitors.values())

    async def get_by_id(
        self,
        monitor_id: UUID,
    ) -> Monitor | None:
        return self._monitors.get(monitor_id)

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
