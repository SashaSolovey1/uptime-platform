from uuid import UUID

from uptime_platform.incidents.entities import (
    Incident,
    IncidentStatus,
)


class InMemoryIncidentRepository:
    def __init__(self) -> None:
        self._incidents: dict[UUID, Incident] = {}

    async def create(
        self,
        incident: Incident,
    ) -> Incident:
        self._incidents[incident.id] = incident

        return incident

    async def get_by_id(
        self,
        incident_id: UUID,
    ) -> Incident | None:
        return self._incidents.get(incident_id)

    async def get_open_by_monitor_id(
        self,
        monitor_id: UUID,
    ) -> Incident | None:
        for incident in self._incidents.values():
            if (
                incident.monitor_id == monitor_id
                and incident.status is IncidentStatus.OPEN
            ):
                return incident

        return None

    async def get_all(
        self,
        status: IncidentStatus | None,
        monitor_ids: set[UUID],
        limit: int,
    ) -> list[Incident]:
        incidents = [
            incident
            for incident in self._incidents.values()
            if incident.monitor_id in monitor_ids
        ]

        if status is not None:
            incidents = [
                incident for incident in incidents if incident.status is status
            ]

        incidents.sort(
            key=lambda incident: incident.started_at,
            reverse=True,
        )

        return incidents[:limit]

    async def update(
        self,
        incident: Incident,
    ) -> Incident | None:
        if incident.id not in self._incidents:
            return None

        self._incidents[incident.id] = incident

        return incident

    async def get_by_monitor_id(
        self,
        monitor_id: UUID,
        limit: int,
    ) -> list[Incident]:
        incidents = [
            incident
            for incident in self._incidents.values()
            if incident.monitor_id == monitor_id
        ]

        incidents.sort(
            key=lambda incident: incident.started_at,
            reverse=True,
        )

        return incidents[:limit]
