from datetime import UTC, datetime
from uuid import UUID, uuid4

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
from uptime_platform.monitors.entities import (
    HttpMonitorConfig,
    Monitor,
    MonitorStatus,
    MonitorType,
)
from uptime_platform.monitors.in_memory_repository import (
    InMemoryMonitorRepository,
)
from uptime_platform.organizations.constants import (
    DEFAULT_ORGANIZATION_ID,
)

pytestmark = pytest.mark.anyio


def make_service() -> tuple[
    IncidentService,
    InMemoryIncidentRepository,
    InMemoryMonitorRepository,
]:
    incident_repository = InMemoryIncidentRepository()
    monitor_repository = InMemoryMonitorRepository()

    service = IncidentService(
        repository=incident_repository,
        monitor_repository=monitor_repository,
        organization_id=DEFAULT_ORGANIZATION_ID,
    )

    return (
        service,
        incident_repository,
        monitor_repository,
    )


def make_monitor(
    monitor_id: UUID | None = None,
) -> Monitor:
    now = datetime.now(UTC)

    return Monitor(
        id=monitor_id or uuid4(),
        organization_id=DEFAULT_ORGANIZATION_ID,
        name="Production API",
        monitor_type=MonitorType.HTTP,
        config=HttpMonitorConfig(
            url="https://example.com",
        ),
        interval_seconds=60,
        timeout_seconds=5,
        status=MonitorStatus.UP,
        created_at=now,
        next_check_at=now,
    )


def make_incident(
    status: IncidentStatus = IncidentStatus.OPEN,
    monitor_id: UUID | None = None,
) -> Incident:
    now = datetime.now(UTC)

    return Incident(
        id=uuid4(),
        monitor_id=(monitor_id if monitor_id is not None else uuid4()),
        status=status,
        started_at=now,
        resolved_at=(now if status is IncidentStatus.RESOLVED else None),
    )


async def test_get_incident_by_id() -> None:
    (
        service,
        incident_repository,
        monitor_repository,
    ) = make_service()

    monitor = make_monitor()

    incident = make_incident(
        monitor_id=monitor.id,
    )

    await monitor_repository.create(monitor)
    await incident_repository.create(incident)

    result = await service.get_by_id(incident.id)

    assert result == incident


async def test_get_nonexistent_incident_returns_none() -> None:
    (
        service,
        _,
        _,
    ) = make_service()

    result = await service.get_by_id(uuid4())

    assert result is None


async def test_filter_incidents_by_status() -> None:
    (
        service,
        incident_repository,
        monitor_repository,
    ) = make_service()

    open_monitor = make_monitor()
    resolved_monitor = make_monitor()

    open_incident = make_incident(
        status=IncidentStatus.OPEN,
        monitor_id=open_monitor.id,
    )

    resolved_incident = make_incident(
        status=IncidentStatus.RESOLVED,
        monitor_id=resolved_monitor.id,
    )

    await monitor_repository.create(open_monitor)
    await monitor_repository.create(resolved_monitor)

    await incident_repository.create(open_incident)
    await incident_repository.create(resolved_incident)

    incidents = await service.get_all(
        status=IncidentStatus.OPEN,
        monitor_id=None,
        limit=100,
    )

    assert incidents == [open_incident]


async def test_filter_incidents_by_monitor() -> None:
    (
        service,
        incident_repository,
        monitor_repository,
    ) = make_service()

    first_monitor = make_monitor()
    second_monitor = make_monitor()

    first = make_incident(
        monitor_id=first_monitor.id,
    )

    second = make_incident(
        monitor_id=second_monitor.id,
    )

    await monitor_repository.create(first_monitor)
    await monitor_repository.create(second_monitor)

    await incident_repository.create(first)
    await incident_repository.create(second)

    incidents = await service.get_all(
        status=None,
        monitor_id=first_monitor.id,
        limit=100,
    )

    assert incidents == [first]
