from datetime import UTC, datetime
from uuid import uuid4

import pytest

from uptime_platform.incidents.entities import (
    Incident,
    IncidentStatus,
)
from uptime_platform.incidents.in_memory_repository import (
    InMemoryIncidentRepository,
)
from uptime_platform.incidents.service import (
    IncidentService,
)

pytestmark = pytest.mark.anyio


def make_incident(
    status: IncidentStatus = IncidentStatus.OPEN,
) -> Incident:
    now = datetime.now(UTC)

    return Incident(
        id=uuid4(),
        monitor_id=uuid4(),
        status=status,
        started_at=now,
        resolved_at=(now if status is IncidentStatus.RESOLVED else None),
    )


async def test_get_incident_by_id() -> None:
    repository = InMemoryIncidentRepository()
    service = IncidentService(repository)

    incident = make_incident()

    await repository.create(incident)

    result = await service.get_by_id(incident.id)

    assert result == incident


async def test_get_nonexistent_incident_returns_none() -> None:
    repository = InMemoryIncidentRepository()
    service = IncidentService(repository)

    result = await service.get_by_id(uuid4())

    assert result is None


async def test_filter_incidents_by_status() -> None:
    repository = InMemoryIncidentRepository()
    service = IncidentService(repository)

    open_incident = make_incident(IncidentStatus.OPEN)

    resolved_incident = make_incident(IncidentStatus.RESOLVED)

    await repository.create(open_incident)

    await repository.create(resolved_incident)

    incidents = await service.get_all(
        status=IncidentStatus.OPEN,
        monitor_id=None,
        limit=100,
    )

    assert incidents == [open_incident]


async def test_filter_incidents_by_monitor() -> None:
    repository = InMemoryIncidentRepository()
    service = IncidentService(repository)

    monitor_id = uuid4()

    first = make_incident()
    first = Incident(
        id=first.id,
        monitor_id=monitor_id,
        status=first.status,
        started_at=first.started_at,
        resolved_at=first.resolved_at,
    )

    second = make_incident()

    await repository.create(first)
    await repository.create(second)

    incidents = await service.get_all(
        status=None,
        monitor_id=monitor_id,
        limit=100,
    )

    assert incidents == [first]
