from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from uptime_platform.monitors.entities import Monitor, MonitorStatus
from uptime_platform.monitors.protocols import MonitorRepositoryProtocol
from uptime_platform.monitors.schemas import MonitorCreate, MonitorUpdate


class MonitorService:
    def __init__(
        self,
        repository: MonitorRepositoryProtocol,
    ) -> None:
        self._repository = repository

    async def create(
        self,
        data: MonitorCreate,
    ) -> Monitor:
        now = datetime.now(UTC)

        monitor = Monitor(
            id=uuid4(),
            status=MonitorStatus.PENDING,
            created_at=now,
            next_check_at=now,
            **data.model_dump(mode="json"),
        )

        return await self._repository.create(monitor)

    async def get_all(self) -> list[Monitor]:
        return await self._repository.get_all()

    async def get_by_id(
        self,
        monitor_id: UUID,
    ) -> Monitor | None:
        return await self._repository.get_by_id(monitor_id)

    async def update(
        self,
        monitor_id: UUID,
        data: MonitorUpdate,
    ) -> Monitor | None:
        monitor = await self._repository.get_by_id(monitor_id)

        if monitor is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True,
            mode="json",
        )

        updated_monitor = replace(
            monitor,
            **update_data,
        )

        return await self._repository.update(updated_monitor)

    async def delete(
        self,
        monitor_id: UUID,
    ) -> bool:
        return await self._repository.delete(monitor_id)
