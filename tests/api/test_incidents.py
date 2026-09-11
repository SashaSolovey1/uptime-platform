from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import httpx2
import pytest

from uptime_platform.auth.dependencies import (
    get_organization_context,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.incidents.dependencies import (
    get_incident_service,
)
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
from uptime_platform.main import app
from uptime_platform.monitors.entities import (
    HttpMonitorConfig,
    Monitor,
    MonitorStatus,
    MonitorType,
)
from uptime_platform.monitors.in_memory_repository import (
    InMemoryMonitorRepository,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def incident_repository() -> InMemoryIncidentRepository:
    return InMemoryIncidentRepository()


@pytest.fixture
def monitor_repository() -> InMemoryMonitorRepository:
    return InMemoryMonitorRepository()


@pytest.fixture
async def client(
    incident_repository: InMemoryIncidentRepository,
    monitor_repository: InMemoryMonitorRepository,
    organization_context: OrganizationContext,
) -> AsyncIterator[httpx2.AsyncClient]:
    app.dependency_overrides[get_organization_context] = lambda: organization_context

    def override_incident_service() -> IncidentService:
        return IncidentService(
            repository=incident_repository,
            monitor_repository=monitor_repository,
            organization_id=(organization_context.organization.id),
        )

    app.dependency_overrides[get_incident_service] = override_incident_service

    transport = httpx2.ASGITransport(
        app=app,
    )

    async with httpx2.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


def make_monitor(
    organization_id: UUID,
    monitor_id: UUID | None = None,
) -> Monitor:
    now = datetime.now(UTC)

    return Monitor(
        id=monitor_id or uuid4(),
        organization_id=organization_id,
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
    monitor_id: UUID,
    status: IncidentStatus = IncidentStatus.OPEN,
) -> Incident:
    now = datetime.now(UTC)

    return Incident(
        id=uuid4(),
        monitor_id=monitor_id,
        status=status,
        started_at=now,
        resolved_at=(now if status is IncidentStatus.RESOLVED else None),
    )


async def test_list_incidents(
    client: httpx2.AsyncClient,
    incident_repository: InMemoryIncidentRepository,
    monitor_repository: InMemoryMonitorRepository,
    organization_context: OrganizationContext,
) -> None:
    first_monitor = make_monitor(organization_context.organization.id)

    second_monitor = make_monitor(organization_context.organization.id)

    first = make_incident(
        monitor_id=first_monitor.id,
    )

    second = make_incident(
        monitor_id=second_monitor.id,
        status=IncidentStatus.RESOLVED,
    )

    await monitor_repository.create(first_monitor)
    await monitor_repository.create(second_monitor)

    await incident_repository.create(first)
    await incident_repository.create(second)

    response = await client.get("/api/v1/incidents")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    incident_ids = {item["id"] for item in data}

    assert incident_ids == {
        str(first.id),
        str(second.id),
    }


async def test_filter_incidents_by_status(
    client: httpx2.AsyncClient,
    incident_repository: InMemoryIncidentRepository,
    monitor_repository: InMemoryMonitorRepository,
    organization_context: OrganizationContext,
) -> None:
    open_monitor = make_monitor(organization_context.organization.id)

    resolved_monitor = make_monitor(organization_context.organization.id)

    open_incident = make_incident(
        monitor_id=open_monitor.id,
        status=IncidentStatus.OPEN,
    )

    resolved_incident = make_incident(
        monitor_id=resolved_monitor.id,
        status=IncidentStatus.RESOLVED,
    )

    await monitor_repository.create(open_monitor)
    await monitor_repository.create(resolved_monitor)

    await incident_repository.create(open_incident)
    await incident_repository.create(resolved_incident)

    response = await client.get(
        "/api/v1/incidents",
        params={
            "status": "open",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == str(open_incident.id)
    assert data[0]["status"] == "open"


async def test_filter_incidents_by_monitor(
    client: httpx2.AsyncClient,
    incident_repository: InMemoryIncidentRepository,
    monitor_repository: InMemoryMonitorRepository,
    organization_context: OrganizationContext,
) -> None:
    matching_monitor = make_monitor(organization_context.organization.id)

    other_monitor = make_monitor(organization_context.organization.id)

    matching_incident = make_incident(
        monitor_id=matching_monitor.id,
    )

    other_incident = make_incident(
        monitor_id=other_monitor.id,
    )

    await monitor_repository.create(matching_monitor)
    await monitor_repository.create(other_monitor)

    await incident_repository.create(matching_incident)
    await incident_repository.create(other_incident)

    response = await client.get(
        "/api/v1/incidents",
        params={
            "monitor_id": str(matching_monitor.id),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["id"] == str(matching_incident.id)

    assert data[0]["monitor_id"] == str(matching_monitor.id)


async def test_get_incident(
    client: httpx2.AsyncClient,
    incident_repository: InMemoryIncidentRepository,
    monitor_repository: InMemoryMonitorRepository,
    organization_context: OrganizationContext,
) -> None:
    monitor = make_monitor(organization_context.organization.id)

    incident = make_incident(
        monitor_id=monitor.id,
    )

    await monitor_repository.create(monitor)

    await incident_repository.create(incident)

    response = await client.get(f"/api/v1/incidents/{incident.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(incident.id)

    assert data["monitor_id"] == str(incident.monitor_id)

    assert data["status"] == "open"
    assert data["resolved_at"] is None


async def test_get_nonexistent_incident_returns_404(
    client: httpx2.AsyncClient,
) -> None:
    response = await client.get(f"/api/v1/incidents/{uuid4()}")

    assert response.status_code == 404

    assert response.json() == {"detail": "Incident not found"}


async def test_invalid_incident_status_returns_422(
    client: httpx2.AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/incidents",
        params={
            "status": "banana",
        },
    )

    assert response.status_code == 422
