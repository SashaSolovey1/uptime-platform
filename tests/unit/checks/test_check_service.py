from datetime import UTC, datetime
from uuid import uuid4

import pytest

from uptime_platform.checks.entities import CheckResult
from uptime_platform.checks.in_memory_repository import InMemoryCheckRepository
from uptime_platform.checks.service import CheckService
from uptime_platform.monitors.entities import (
    Monitor,
    MonitorStatus,
)
from uptime_platform.monitors.in_memory_repository import (
    InMemoryMonitorRepository,
)

pytestmark = pytest.mark.anyio


class StubHttpChecker:
    def __init__(
        self,
        result: CheckResult,
    ) -> None:
        self._result = result
        self.calls = 0

    async def check(
        self,
        url: str,
        timeout_seconds: int,
    ) -> CheckResult:
        self.calls += 1

        return self._result


def make_monitor(
    status: MonitorStatus = MonitorStatus.PENDING,
    consecutive_failures: int = 0,
    consecutive_successes: int = 0,
) -> Monitor:
    now = datetime.now(UTC)

    return Monitor(
        id=uuid4(),
        name="Production API",
        url="https://example.com",
        interval_seconds=60,
        timeout_seconds=5,
        status=status,
        created_at=now,
        next_check_at=now,
        failure_threshold=3,
        recovery_threshold=2,
        consecutive_failures=consecutive_failures,
        consecutive_successes=consecutive_successes,
    )


async def test_successful_check_changes_monitor_to_up() -> None:
    monitor_repository = InMemoryMonitorRepository()
    check_repository = InMemoryCheckRepository()

    checker = StubHttpChecker(
        CheckResult(
            success=True,
            response_time_ms=42.0,
            status_code=200,
            error=None,
        )
    )

    monitor = make_monitor()

    await monitor_repository.create(monitor)

    service = CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        checker=checker,
    )

    check = await service.run(monitor.id)

    updated_monitor = await monitor_repository.get_by_id(monitor.id)

    assert check is not None
    assert check.monitor_id == monitor.id
    assert check.success is True
    assert check.response_time_ms == 42.0
    assert check.status_code == 200
    assert check.error is None

    assert updated_monitor is not None
    assert updated_monitor.status is MonitorStatus.UP

    assert checker.calls == 1


async def test_first_success_does_not_recover_down_monitor() -> None:
    monitor_repository = InMemoryMonitorRepository()
    check_repository = InMemoryCheckRepository()

    checker = StubHttpChecker(
        CheckResult(
            success=True,
            response_time_ms=50.0,
            status_code=200,
            error=None,
        )
    )

    monitor = make_monitor(status=MonitorStatus.DOWN)

    await monitor_repository.create(monitor)

    service = CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        checker=checker,
    )

    await service.run(monitor.id)

    updated_monitor = await monitor_repository.get_by_id(monitor.id)

    assert updated_monitor is not None
    assert updated_monitor.status is MonitorStatus.DOWN
    assert updated_monitor.consecutive_successes == 1
    assert updated_monitor.consecutive_failures == 0


async def test_first_success_does_not_recover_down_monitor() -> None:
    monitor_repository = InMemoryMonitorRepository()
    check_repository = InMemoryCheckRepository()

    checker = StubHttpChecker(
        CheckResult(
            success=True,
            response_time_ms=50.0,
            status_code=200,
            error=None,
        )
    )

    monitor = make_monitor(status=MonitorStatus.DOWN)

    await monitor_repository.create(monitor)

    service = CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        checker=checker,
    )

    await service.run(monitor.id)

    updated_monitor = await monitor_repository.get_by_id(monitor.id)

    assert updated_monitor is not None
    assert updated_monitor.status is MonitorStatus.DOWN
    assert updated_monitor.consecutive_successes == 1
    assert updated_monitor.consecutive_failures == 0


async def test_second_success_recovers_down_monitor() -> None:
    monitor_repository = InMemoryMonitorRepository()
    check_repository = InMemoryCheckRepository()

    checker = StubHttpChecker(
        CheckResult(
            success=True,
            response_time_ms=50.0,
            status_code=200,
            error=None,
        )
    )

    monitor = make_monitor(
        status=MonitorStatus.DOWN,
        consecutive_successes=1,
    )

    await monitor_repository.create(monitor)

    service = CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        checker=checker,
    )

    await service.run(monitor.id)

    updated_monitor = await monitor_repository.get_by_id(monitor.id)

    assert updated_monitor is not None
    assert updated_monitor.status is MonitorStatus.UP
    assert updated_monitor.consecutive_successes == 2
    assert updated_monitor.consecutive_failures == 0


async def test_failed_check_keeps_down_monitor_down() -> None:
    monitor_repository = InMemoryMonitorRepository()
    check_repository = InMemoryCheckRepository()

    checker = StubHttpChecker(
        CheckResult(
            success=False,
            response_time_ms=1000.0,
            status_code=503,
            error=None,
        )
    )

    monitor = make_monitor(status=MonitorStatus.DOWN)

    await monitor_repository.create(monitor)

    service = CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        checker=checker,
    )

    await service.run(monitor.id)

    updated_monitor = await monitor_repository.get_by_id(monitor.id)

    assert updated_monitor is not None
    assert updated_monitor.status is MonitorStatus.DOWN


async def test_paused_monitor_keeps_paused_status() -> None:
    monitor_repository = InMemoryMonitorRepository()
    check_repository = InMemoryCheckRepository()

    checker = StubHttpChecker(
        CheckResult(
            success=True,
            response_time_ms=30.0,
            status_code=200,
            error=None,
        )
    )

    monitor = make_monitor(status=MonitorStatus.PAUSED)

    await monitor_repository.create(monitor)

    service = CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        checker=checker,
    )

    await service.run(monitor.id)

    updated_monitor = await monitor_repository.get_by_id(monitor.id)

    assert updated_monitor is not None
    assert updated_monitor.status is MonitorStatus.PAUSED


async def test_nonexistent_monitor_is_not_checked() -> None:
    monitor_repository = InMemoryMonitorRepository()
    check_repository = InMemoryCheckRepository()

    checker = StubHttpChecker(
        CheckResult(
            success=True,
            response_time_ms=42.0,
            status_code=200,
            error=None,
        )
    )

    service = CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        checker=checker,
    )

    result = await service.run(uuid4())

    assert result is None
    assert checker.calls == 0


async def test_check_is_saved_to_history() -> None:
    monitor_repository = InMemoryMonitorRepository()
    check_repository = InMemoryCheckRepository()

    checker = StubHttpChecker(
        CheckResult(
            success=True,
            response_time_ms=42.0,
            status_code=200,
            error=None,
        )
    )

    monitor = make_monitor()

    await monitor_repository.create(monitor)

    service = CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        checker=checker,
    )

    await service.run(monitor.id)

    history = await service.get_history(
        monitor_id=monitor.id,
        limit=50,
    )

    assert history is not None
    assert len(history) == 1

    check = history[0]

    assert check.monitor_id == monitor.id
    assert check.success is True
    assert check.status_code == 200


async def test_get_history_returns_none_for_nonexistent_monitor() -> None:
    monitor_repository = InMemoryMonitorRepository()
    check_repository = InMemoryCheckRepository()

    checker = StubHttpChecker(
        CheckResult(
            success=True,
            response_time_ms=42.0,
            status_code=200,
            error=None,
        )
    )

    service = CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        checker=checker,
    )

    history = await service.get_history(
        monitor_id=uuid4(),
        limit=50,
    )

    assert history is None


async def test_third_failure_marks_monitor_down() -> None:
    monitor_repository = InMemoryMonitorRepository()
    check_repository = InMemoryCheckRepository()

    checker = StubHttpChecker(
        CheckResult(
            success=False,
            response_time_ms=2000.0,
            status_code=None,
            error="Connection failed",
        )
    )

    monitor = make_monitor(
        status=MonitorStatus.UP,
        consecutive_failures=2,
    )

    await monitor_repository.create(monitor)

    service = CheckService(
        monitor_repository=monitor_repository,
        check_repository=check_repository,
        checker=checker,
    )

    await service.run(monitor.id)

    updated_monitor = await monitor_repository.get_by_id(monitor.id)

    assert updated_monitor is not None
    assert updated_monitor.status is MonitorStatus.DOWN
    assert updated_monitor.consecutive_failures == 3
    assert updated_monitor.consecutive_successes == 0
