from datetime import datetime
from typing import Protocol
from uuid import UUID

from uptime_platform.maintenance.entities import (
    MaintenanceWindow,
)


class MaintenanceWindowRepositoryProtocol(Protocol):
    async def create(
        self,
        window: MaintenanceWindow,
    ) -> MaintenanceWindow: ...

    async def get_by_id(
        self,
        window_id: UUID,
    ) -> MaintenanceWindow | None: ...

    async def get_all(
        self,
        monitor_id: UUID | None = None,
    ) -> list[MaintenanceWindow]: ...

    async def get_active(
        self,
        monitor_id: UUID,
        now: datetime,
    ) -> MaintenanceWindow | None: ...

    async def delete(
        self,
        window_id: UUID,
    ) -> bool: ...
