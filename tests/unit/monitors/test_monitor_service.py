from uuid import UUID, uuid4

import pytest

from uptime_platform.monitors.entities import MonitorStatus
from uptime_platform.monitors.in_memory_repository import InMemoryMonitorRepository
from uptime_platform.monitors.schemas import (
    MonitorCreate,
    MonitorUpdate,
)
from uptime_platform.monitors.service import MonitorService

pytestmark = pytest.mark.anyio


@pytest.fixture
def service() -> MonitorService:
    repository = InMemoryMonitorRepository()
    return MonitorService(repository)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def test_create_monitor(
    service: MonitorService,
) -> None:
    data = MonitorCreate(
        name="Production API",
        url="https://example.com/health",
        interval_seconds=30,
        timeout_seconds=5,
    )

    monitor = await service.create(data)

    assert isinstance(monitor.id, UUID)
    assert monitor.name == "Production API"
    assert monitor.url == "https://example.com/health"
    assert monitor.interval_seconds == 30
    assert monitor.timeout_seconds == 5
    assert monitor.status == MonitorStatus.PENDING
    assert monitor.created_at.tzinfo is not None


async def test_get_monitor_by_id(
    service: MonitorService,
) -> None:
    created_monitor = await service.create(
        MonitorCreate(
            name="Production API",
            url="https://example.com/health",
        )
    )

    found_monitor = await service.get_by_id(created_monitor.id)

    assert found_monitor is not None
    assert found_monitor.id == created_monitor.id


async def test_get_nonexistent_monitor_returns_none(
    service: MonitorService,
) -> None:
    monitor = await service.get_by_id(uuid4())

    assert monitor is None


async def test_update_monitor(
    service: MonitorService,
) -> None:
    created_monitor = await service.create(
        MonitorCreate(
            name="Production API",
            url="https://example.com/health",
            interval_seconds=30,
            timeout_seconds=5,
        )
    )

    updated_monitor = await service.update(
        created_monitor.id,
        MonitorUpdate(
            timeout_seconds=15,
        ),
    )

    assert updated_monitor is not None
    assert updated_monitor.id == created_monitor.id
    assert updated_monitor.name == "Production API"
    assert updated_monitor.interval_seconds == 30
    assert updated_monitor.timeout_seconds == 15


async def test_delete_monitor(
    service: MonitorService,
) -> None:
    created_monitor = await service.create(
        MonitorCreate(
            name="Production API",
            url="https://example.com/health",
        )
    )

    deleted = await service.delete(created_monitor.id)

    assert deleted is True

    monitor = await service.get_by_id(created_monitor.id)

    assert monitor is None
