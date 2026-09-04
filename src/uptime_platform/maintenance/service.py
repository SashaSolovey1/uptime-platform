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
    ) -> None:
        self._repository = repository
        self._monitor_repository = monitor_repository

    async def create(
        self,
        data: MaintenanceWindowCreate,
    ) -> MaintenanceWindow | None:
        monitor = await self._monitor_repository.get_by_id(data.monitor_id)

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
        return await self._repository.get_all(monitor_id=monitor_id)

    async def get(
        self,
        window_id: UUID,
    ) -> MaintenanceWindow | None:
        return await self._repository.get_by_id(window_id)

    async def delete(
        self,
        window_id: UUID,
    ) -> bool:
        return await self._repository.delete(window_id)
