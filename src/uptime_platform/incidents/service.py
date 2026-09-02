from uuid import UUID

from uptime_platform.incidents.entities import (
    Incident,
    IncidentStatus,
)
from uptime_platform.incidents.protocols import (
    IncidentRepositoryProtocol,
)


class IncidentService:
    def __init__(
        self,
        repository: IncidentRepositoryProtocol,
    ) -> None:
        self._repository = repository

    async def get_all(
        self,
        status: IncidentStatus | None,
        monitor_id: UUID | None,
        limit: int,
    ) -> list[Incident]:
        return await self._repository.get_all(
            status=status,
            monitor_id=monitor_id,
            limit=limit,
        )

    async def get_by_id(
        self,
        incident_id: UUID,
    ) -> Incident | None:
        return await self._repository.get_by_id(incident_id)
