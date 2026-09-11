from uuid import UUID

from uptime_platform.incidents.entities import (
    Incident,
    IncidentStatus,
)
from uptime_platform.incidents.protocols import (
    IncidentRepositoryProtocol,
)
from uptime_platform.monitors.protocols import (
    MonitorRepositoryProtocol,
)


class IncidentService:
    def __init__(
        self,
        repository: IncidentRepositoryProtocol,
        monitor_repository: MonitorRepositoryProtocol,
        organization_id: UUID,
    ) -> None:
        self._repository = repository
        self._monitor_repository = monitor_repository
        self._organization_id = organization_id

    async def get_all(
        self,
        status: IncidentStatus | None,
        monitor_id: UUID | None,
        limit: int,
    ) -> list[Incident]:
        monitors = await self._monitor_repository.get_all(self._organization_id)

        monitor_ids = {monitor.id for monitor in monitors}

        if monitor_id is not None:
            if monitor_id not in monitor_ids:
                return []

            monitor_ids = {monitor_id}

        return await self._repository.get_all(
            status=status,
            monitor_ids=monitor_ids,
            limit=limit,
        )

    async def get_by_id(
        self,
        incident_id: UUID,
    ) -> Incident | None:
        incident = await self._repository.get_by_id(incident_id)

        if incident is None:
            return None

        monitor = await self._monitor_repository.get_by_id(
            incident.monitor_id,
            self._organization_id,
        )

        if monitor is None:
            return None

        return incident
