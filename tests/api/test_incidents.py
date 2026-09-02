from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import httpx2
import pytest

from uptime_platform.incidents.dependencies import (
    get_incident_repository,
)
from uptime_platform.incidents.entities import (
    Incident,
    IncidentStatus,
)
from uptime_platform.incidents.in_memory_repository import (
    InMemoryIncidentRepository,
)
from uptime_platform.main import app

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository() -> InMemoryIncidentRepository:
    return InMemoryIncidentRepository()


@pytest.fixture
async def client(
    repository: InMemoryIncidentRepository,
) -> AsyncIterator[httpx2.AsyncClient]:
    def override_incident_repository() -> InMemoryIncidentRepository:
        return repository

    app.dependency_overrides[get_incident_repository] = override_incident_repository

    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


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


async def test_list_incidents(
    client: httpx2.AsyncClient,
    repository: InMemoryIncidentRepository,
) -> None:
    first = make_incident()

    second = make_incident(status=IncidentStatus.RESOLVED)

    await repository.create(first)
    await repository.create(second)

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
    repository: InMemoryIncidentRepository,
) -> None:
    open_incident = make_incident(status=IncidentStatus.OPEN)

    resolved_incident = make_incident(status=IncidentStatus.RESOLVED)

    await repository.create(open_incident)

    await repository.create(resolved_incident)

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
    repository: InMemoryIncidentRepository,
) -> None:
    monitor_id = uuid4()

    matching_incident = make_incident(monitor_id=monitor_id)

    other_incident = make_incident()

    await repository.create(matching_incident)

    await repository.create(other_incident)

    response = await client.get(
        "/api/v1/incidents",
        params={
            "monitor_id": str(monitor_id),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == str(matching_incident.id)
    assert data[0]["monitor_id"] == str(monitor_id)


async def test_get_incident(
    client: httpx2.AsyncClient,
    repository: InMemoryIncidentRepository,
) -> None:
    incident = make_incident()

    await repository.create(incident)

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
