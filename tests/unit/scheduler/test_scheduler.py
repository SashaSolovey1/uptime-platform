from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from uptime_platform.checks.service import CheckService
from uptime_platform.monitors.entities import (
    HttpMonitorConfig,
    Monitor,
    MonitorStatus,
    MonitorType,
)
from uptime_platform.scheduler.scheduler import Scheduler

pytestmark = pytest.mark.anyio


class FakeSession:
    def __init__(self) -> None:
        self.commit = AsyncMock()
        self.rollback = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        pass


def fake_session_factory() -> FakeSession:
    return FakeSession()


def make_monitor(
    status: MonitorStatus = MonitorStatus.PENDING,
) -> Monitor:
    now = datetime.now(UTC)

    return Monitor(
        id=uuid4(),
        name="Test monitor",
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


async def test_scheduler_can_process_due_monitor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monitor = make_monitor()

    checker = MagicMock()
    checker.check = AsyncMock(
        return_value=MagicMock(),
    )

    checker_factory = MagicMock()
    checker_factory.create.return_value = checker

    scheduler = Scheduler(
        session_factory=fake_session_factory,
        checker_factory=checker_factory,
    )

    monkeypatch.setattr(
        scheduler,
        "_get_due_monitors",
        AsyncMock(return_value=[monitor]),
    )

    record_mock = AsyncMock()

    monkeypatch.setattr(
        CheckService,
        "record",
        record_mock,
    )

    processed = await scheduler.run_once()

    assert processed == 1

    checker_factory.create.assert_called_once_with(monitor)

    checker.check.assert_awaited_once_with(
        timeout_seconds=monitor.timeout_seconds,
    )

    record_mock.assert_awaited_once_with(
        monitor_id=monitor.id,
        result=checker.check.return_value,
    )
