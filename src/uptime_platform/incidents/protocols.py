from typing import Protocol
from uuid import UUID

from uptime_platform.incidents.entities import (
    Incident,
    IncidentStatus,
)


class IncidentRepositoryProtocol(Protocol):
    async def create(
        self,
        incident: Incident,
    ) -> Incident: ...

    async def get_by_id(
        self,
        incident_id: UUID,
    ) -> Incident | None: ...

    async def get_open_by_monitor_id(
        self,
        monitor_id: UUID,
    ) -> Incident | None: ...

    async def get_all(
        self,
        status: IncidentStatus | None,
        monitor_ids: set[UUID],
        limit: int,
    ) -> list[Incident]: ...

    async def update(
        self,
        incident: Incident,
    ) -> Incident | None: ...

    async def get_by_monitor_id(
        self,
        monitor_id: UUID,
        limit: int,
    ) -> list[Incident]: ...
