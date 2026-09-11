from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

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
from uptime_platform.statistics.entities import (
    MonitorStatistics,
)
from uptime_platform.statistics.schemas import (
    StatisticsPeriod,
)
from uptime_platform.statistics.service import (
    StatisticsService,
)

pytestmark = pytest.mark.anyio


class StubStatisticsRepository:
    def __init__(self) -> None:
        self.starts_at: datetime | None = None
        self.ends_at: datetime | None = None

    async def get_monitor_statistics(
        self,
        monitor_id: UUID,
        starts_at: datetime,
        ends_at: datetime,
    ) -> MonitorStatistics:
        self.starts_at = starts_at
        self.ends_at = ends_at

        return MonitorStatistics(
            monitor_id=monitor_id,
            starts_at=starts_at,
            ends_at=ends_at,
            total_checks=10,
            successful_checks=9,
            failed_checks=1,
            uptime_percentage=90.0,
            average_response_time_ms=42.0,
        )


def make_monitor(
    status: MonitorStatus = MonitorStatus.PENDING,
    organization_id: UUID = DEFAULT_ORGANIZATION_ID,
) -> Monitor:
    now = datetime.now(UTC)

    return Monitor(
        id=uuid4(),
        organization_id=organization_id,
        name="API",
        monitor_type=MonitorType.HTTP,
        config=HttpMonitorConfig(
            url="https://example.com",
        ),
        interval_seconds=60,
        timeout_seconds=5,
        status=status,
        created_at=now,
        next_check_at=now,
        failure_threshold=3,
        recovery_threshold=2,
        consecutive_failures=0,
        consecutive_successes=0,
    )


async def test_get_24h_statistics() -> None:
    monitor_repository = InMemoryMonitorRepository()

    statistics_repository = StubStatisticsRepository()

    monitor = make_monitor()

    await monitor_repository.create(monitor)

    service = StatisticsService(
        repository=statistics_repository,
        monitor_repository=monitor_repository,
        organization_id=DEFAULT_ORGANIZATION_ID,
    )

    result = await service.get_monitor_statistics(
        monitor.id,
        StatisticsPeriod.HOURS_24,
    )

    assert result is not None

    assert statistics_repository.starts_at is not None
    assert statistics_repository.ends_at is not None

    duration = statistics_repository.ends_at - statistics_repository.starts_at

    assert duration.total_seconds() == 86400


async def test_statistics_for_nonexistent_monitor_returns_none() -> None:
    service = StatisticsService(
        repository=StubStatisticsRepository(),
        monitor_repository=(InMemoryMonitorRepository()),
        organization_id=DEFAULT_ORGANIZATION_ID,
    )

    result = await service.get_monitor_statistics(
        uuid4(),
        StatisticsPeriod.HOURS_24,
    )

    assert result is None


async def test_get_custom_range_statistics() -> None:
    monitor_repository = InMemoryMonitorRepository()

    statistics_repository = StubStatisticsRepository()

    monitor = make_monitor()

    await monitor_repository.create(monitor)

    service = StatisticsService(
        repository=statistics_repository,
        monitor_repository=monitor_repository,
        organization_id=DEFAULT_ORGANIZATION_ID,
    )

    starts_at = datetime(
        2026,
        9,
        1,
        tzinfo=UTC,
    )

    ends_at = datetime(
        2026,
        9,
        5,
        tzinfo=UTC,
    )

    result = await service.get_monitor_statistics(
        monitor_id=monitor.id,
        starts_at=starts_at,
        ends_at=ends_at,
    )

    assert result is not None

    assert statistics_repository.starts_at == starts_at
    assert statistics_repository.ends_at == ends_at


async def test_default_statistics_period_is_24_hours() -> None:
    monitor_repository = InMemoryMonitorRepository()

    statistics_repository = StubStatisticsRepository()

    monitor = make_monitor()

    await monitor_repository.create(monitor)

    service = StatisticsService(
        repository=statistics_repository,
        monitor_repository=monitor_repository,
        organization_id=DEFAULT_ORGANIZATION_ID,
    )

    result = await service.get_monitor_statistics(monitor_id=monitor.id)

    assert result is not None

    assert statistics_repository.starts_at is not None
    assert statistics_repository.ends_at is not None

    duration = statistics_repository.ends_at - statistics_repository.starts_at

    assert duration == timedelta(hours=24)
