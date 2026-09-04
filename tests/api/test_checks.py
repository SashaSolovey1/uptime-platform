from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

import httpx2
import pytest

from uptime_platform.checks.dependencies import (
    get_check_service,
)
from uptime_platform.checks.entities import CheckResult
from uptime_platform.checks.in_memory_repository import (
    InMemoryCheckRepository,
)
from uptime_platform.checks.service import CheckService
from uptime_platform.incidents.in_memory_repository import (
    InMemoryIncidentRepository,
)
from uptime_platform.main import app
from uptime_platform.maintenance.in_memory_repository import (
    InMemoryMaintenanceWindowRepository,
)
from uptime_platform.monitors.entities import (
    Monitor,
    MonitorStatus,
)
from uptime_platform.monitors.in_memory_repository import (
    InMemoryMonitorRepository,
)
from uptime_platform.outbox.in_memory_repository import (
    InMemoryOutboxRepository,
)

pytestmark = pytest.mark.anyio


class StubHttpChecker:
    async def check(
        self,
        url: str,
        timeout_seconds: int,
    ) -> CheckResult:
        return CheckResult(
            success=True,
            response_time_ms=42.5,
            status_code=200,
            error=None,
        )


@pytest.fixture
def monitor_repository() -> InMemoryMonitorRepository:
    return InMemoryMonitorRepository()


@pytest.fixture
def check_repository() -> InMemoryCheckRepository:
    return InMemoryCheckRepository()


@pytest.fixture
def incident_repository() -> InMemoryIncidentRepository:
    return InMemoryIncidentRepository()


@pytest.fixture
def outbox_repository() -> InMemoryOutboxRepository:
    return InMemoryOutboxRepository()


@pytest.fixture
def maintenance_repository() -> InMemoryMaintenanceWindowRepository:
    return InMemoryMaintenanceWindowRepository()


@pytest.fixture
async def client(
    monitor_repository: InMemoryMonitorRepository,
    check_repository: InMemoryCheckRepository,
    incident_repository: InMemoryIncidentRepository,
    outbox_repository: InMemoryOutboxRepository,
    maintenance_repository: InMemoryMaintenanceWindowRepository,
) -> AsyncIterator[httpx2.AsyncClient]:
    def override_check_service() -> CheckService:
        return CheckService(
            monitor_repository=monitor_repository,
            check_repository=check_repository,
            incident_repository=incident_repository,
            outbox_repository=outbox_repository,
            maintenance_repository=maintenance_repository,
            checker=StubHttpChecker(),
        )

    app.dependency_overrides[get_check_service] = override_check_service

    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


async def create_monitor(
    repository: InMemoryMonitorRepository,
) -> Monitor:
    now = datetime.now(UTC)

    monitor = Monitor(
        id=uuid4(),
        name="Test monitor",
        url="https://example.com",
        interval_seconds=60,
        timeout_seconds=5,
        status=MonitorStatus.PENDING,
        created_at=now,
        next_check_at=now,
        failure_threshold=3,
        recovery_threshold=2,
        consecutive_failures=0,
        consecutive_successes=0,
    )

    await repository.create(monitor)

    return monitor


async def test_run_check(
    client: httpx2.AsyncClient,
    monitor_repository: InMemoryMonitorRepository,
) -> None:
    monitor = await create_monitor(monitor_repository)

    response = await client.post(f"/api/v1/monitors/{monitor.id}/checks")

    assert response.status_code == 201

    data = response.json()

    assert data["monitor_id"] == str(monitor.id)
    assert data["success"] is True
    assert data["response_time_ms"] == 42.5
    assert data["status_code"] == 200
    assert data["error"] is None
    assert "id" in data
    assert "checked_at" in data


async def test_run_check_for_nonexistent_monitor_returns_404(
    client: httpx2.AsyncClient,
) -> None:
    monitor_id = uuid4()

    response = await client.post(f"/api/v1/monitors/{monitor_id}/checks")

    assert response.status_code == 404


async def test_get_check_history(
    client: httpx2.AsyncClient,
    monitor_repository: InMemoryMonitorRepository,
) -> None:
    monitor = await create_monitor(monitor_repository)

    await client.post(f"/api/v1/monitors/{monitor.id}/checks")

    await client.post(f"/api/v1/monitors/{monitor.id}/checks")

    response = await client.get(f"/api/v1/monitors/{monitor.id}/checks")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert all(check["monitor_id"] == str(monitor.id) for check in data)

    assert all(check["success"] is True for check in data)


async def test_get_check_history_respects_limit(
    client: httpx2.AsyncClient,
    monitor_repository: InMemoryMonitorRepository,
) -> None:
    monitor = await create_monitor(monitor_repository)

    await client.post(f"/api/v1/monitors/{monitor.id}/checks")

    await client.post(f"/api/v1/monitors/{monitor.id}/checks")

    await client.post(f"/api/v1/monitors/{monitor.id}/checks")

    response = await client.get(
        f"/api/v1/monitors/{monitor.id}/checks",
        params={
            "limit": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


async def test_get_check_history_for_nonexistent_monitor_returns_404(
    client: httpx2.AsyncClient,
) -> None:
    monitor_id = uuid4()

    response = await client.get(f"/api/v1/monitors/{monitor_id}/checks")

    assert response.status_code == 404


async def test_invalid_check_history_limit_returns_422(
    client: httpx2.AsyncClient,
    monitor_repository: InMemoryMonitorRepository,
) -> None:
    monitor = await create_monitor(monitor_repository)

    response = await client.get(
        f"/api/v1/monitors/{monitor.id}/checks",
        params={
            "limit": 0,
        },
    )

    assert response.status_code == 422
