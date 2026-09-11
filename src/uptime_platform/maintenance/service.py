from datetime import UTC, datetime
from uuid import UUID, uuid4

from uptime_platform.maintenance.entities import (
    MaintenanceWindow,
)
from uptime_platform.maintenance.protocols import (
    MaintenanceWindowRepositoryProtocol,
)
from uptime_platform.maintenance.schemas import (
    MaintenanceWindowCreate,
)
from uptime_platform.monitors.protocols import (
    MonitorRepositoryProtocol,
)


class MaintenanceWindowService:
    def __init__(
        self,
        repository: MaintenanceWindowRepositoryProtocol,
        monitor_repository: MonitorRepositoryProtocol,
        organization_id: UUID,
    ) -> None:
        self._repository = repository
        self._monitor_repository = monitor_repository
        self._organization_id = organization_id

    async def create(
        self,
        data: MaintenanceWindowCreate,
    ) -> MaintenanceWindow | None:
        monitor = await self._monitor_repository.get_by_id(
            data.monitor_id,
            self._organization_id,
        )

        if monitor is None:
            return None

        window = MaintenanceWindow(
            id=uuid4(),
            monitor_id=data.monitor_id,
            starts_at=data.starts_at,
            ends_at=data.ends_at,
            reason=data.reason,
            created_at=datetime.now(UTC),
        )

        return await self._repository.create(window)

    async def get_all(
        self,
        monitor_id: UUID | None = None,
    ) -> list[MaintenanceWindow]:
        monitors = await self._monitor_repository.get_all(self._organization_id)

        monitor_ids = {monitor.id for monitor in monitors}

        if monitor_id is not None:
            if monitor_id not in monitor_ids:
                return []

            monitor_ids = {monitor_id}

        return await self._repository.get_all(monitor_ids=monitor_ids)

    async def get(
        self,
        window_id: UUID,
    ) -> MaintenanceWindow | None:
        window = await self._repository.get_by_id(window_id)

        if window is None:
            return None

        monitor = await self._monitor_repository.get_by_id(
            window.monitor_id,
            self._organization_id,
        )

        if monitor is None:
            return None

        return window

    async def delete(
        self,
        window_id: UUID,
    ) -> bool:
        window = await self.get(window_id)

        if window is None:
            return False

        return await self._repository.delete(window_id)
