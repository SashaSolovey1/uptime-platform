from datetime import UTC, datetime
from uuid import uuid4

from uptime_platform.monitors.entities import (
    Monitor,
    MonitorStatus,
)
from uptime_platform.monitors.state import (
    apply_check_result,
)


def make_monitor(
    status: MonitorStatus,
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


def test_pending_monitor_becomes_up_after_success() -> None:
    monitor = make_monitor(MonitorStatus.PENDING)

    result = apply_check_result(
        monitor,
        success=True,
    )

    assert result.status is MonitorStatus.UP
    assert result.consecutive_successes == 1
    assert result.consecutive_failures == 0


def test_monitor_stays_up_before_failure_threshold() -> None:
    monitor = make_monitor(
        MonitorStatus.UP,
        consecutive_failures=1,
    )

    result = apply_check_result(
        monitor,
        success=False,
    )

    assert result.status is MonitorStatus.UP
    assert result.consecutive_failures == 2
    assert result.consecutive_successes == 0


def test_monitor_becomes_down_at_failure_threshold() -> None:
    monitor = make_monitor(
        MonitorStatus.UP,
        consecutive_failures=2,
    )

    result = apply_check_result(
        monitor,
        success=False,
    )

    assert result.status is MonitorStatus.DOWN
    assert result.consecutive_failures == 3


def test_down_monitor_stays_down_before_recovery_threshold() -> None:
    monitor = make_monitor(MonitorStatus.DOWN)

    result = apply_check_result(
        monitor,
        success=True,
    )

    assert result.status is MonitorStatus.DOWN
    assert result.consecutive_successes == 1


def test_down_monitor_recovers_at_recovery_threshold() -> None:
    monitor = make_monitor(
        MonitorStatus.DOWN,
        consecutive_successes=1,
    )

    result = apply_check_result(
        monitor,
        success=True,
    )

    assert result.status is MonitorStatus.UP
    assert result.consecutive_successes == 2


def test_success_resets_failure_counter() -> None:
    monitor = make_monitor(
        MonitorStatus.UP,
        consecutive_failures=2,
    )

    result = apply_check_result(
        monitor,
        success=True,
    )

    assert result.status is MonitorStatus.UP
    assert result.consecutive_failures == 0


def test_failure_resets_success_counter() -> None:
    monitor = make_monitor(
        MonitorStatus.DOWN,
        consecutive_successes=1,
    )

    result = apply_check_result(
        monitor,
        success=False,
    )

    assert result.status is MonitorStatus.DOWN
    assert result.consecutive_successes == 0


def test_paused_monitor_does_not_change() -> None:
    monitor = make_monitor(MonitorStatus.PAUSED)

    result = apply_check_result(
        monitor,
        success=False,
    )

    assert result == monitor
