from datetime import datetime
from uuid import UUID

from uptime_platform.maintenance.entities import (
    MaintenanceWindow,
)


class InMemoryMaintenanceWindowRepository:
    def __init__(self) -> None:
        self._windows: dict[
            UUID,
            MaintenanceWindow,
        ] = {}

    async def create(
        self,
        window: MaintenanceWindow,
    ) -> MaintenanceWindow:
        self._windows[window.id] = window

        return window

    async def get_by_id(
        self,
        window_id: UUID,
    ) -> MaintenanceWindow | None:
        return self._windows.get(window_id)

    async def get_all(
        self,
        monitor_ids: set[UUID],
    ) -> list[MaintenanceWindow]:
        windows = [
            window
            for window in self._windows.values()
            if window.monitor_id in monitor_ids
        ]

        windows.sort(
            key=lambda window: window.starts_at,
            reverse=True,
        )

        return windows

    async def get_active(
        self,
        monitor_id: UUID,
        now: datetime,
    ) -> MaintenanceWindow | None:
        windows = [
            window
            for window in self._windows.values()
            if (window.monitor_id == monitor_id and window.is_active(now))
        ]

        if not windows:
            return None

        return max(
            windows,
            key=lambda window: window.starts_at,
        )

    async def delete(
        self,
        window_id: UUID,
    ) -> bool:
        if window_id not in self._windows:
            return False

        del self._windows[window_id]

        return True
