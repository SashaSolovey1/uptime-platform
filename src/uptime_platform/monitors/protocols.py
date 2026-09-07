from datetime import datetime
from typing import Protocol
from uuid import UUID

from uptime_platform.monitors.entities import Monitor


class MonitorRepositoryProtocol(Protocol):
    async def create(
        self,
        monitor: Monitor,
    ) -> Monitor: ...

    async def get_all(self) -> list[Monitor]: ...

    async def get_by_id(
        self,
        monitor_id: UUID,
    ) -> Monitor | None: ...

    async def update(
        self,
        monitor: Monitor,
    ) -> Monitor | None: ...

    async def delete(
        self,
        monitor_id: UUID,
    ) -> bool: ...

    async def get_due(
        self,
        now: datetime,
        limit: int,
    ) -> list[Monitor]: ...

    async def get_by_id_for_update(
        self,
        monitor_id: UUID,
    ) -> Monitor | None: ...
