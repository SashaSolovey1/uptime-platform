from datetime import UTC, datetime
from uuid import uuid4

from uptime_platform.monitors.entities import (
    HttpMonitorConfig,
    Monitor,
    MonitorStatus,
    MonitorType,
)
from uptime_platform.status_pages.entities import (
    StatusPageStatus,
)
from uptime_platform.status_pages.service import (
    calculate_status_page_status,
)


def make_monitor(
    status: MonitorStatus,
) -> Monitor:
    now = datetime.now(UTC)

    return Monitor(
        id=uuid4(),
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


def test_empty_status_page_is_unknown() -> None:
    status = calculate_status_page_status([])

    assert status is StatusPageStatus.UNKNOWN


def test_all_monitors_up_is_operational() -> None:
    monitors = [
        make_monitor(MonitorStatus.UP),
        make_monitor(MonitorStatus.UP),
    ]

    status = calculate_status_page_status(monitors)

    assert status is StatusPageStatus.OPERATIONAL


def test_one_down_monitor_is_partial_outage() -> None:
    monitors = [
        make_monitor(MonitorStatus.UP),
        make_monitor(MonitorStatus.DOWN),
    ]

    status = calculate_status_page_status(monitors)

    assert status is StatusPageStatus.PARTIAL_OUTAGE


def test_all_monitors_down_is_major_outage() -> None:
    monitors = [
        make_monitor(MonitorStatus.DOWN),
        make_monitor(MonitorStatus.DOWN),
    ]

    status = calculate_status_page_status(monitors)

    assert status is StatusPageStatus.MAJOR_OUTAGE


def test_paused_monitors_are_ignored() -> None:
    monitors = [
        make_monitor(MonitorStatus.UP),
        make_monitor(MonitorStatus.PAUSED),
    ]

    status = calculate_status_page_status(monitors)

    assert status is StatusPageStatus.OPERATIONAL


def test_only_paused_monitors_is_unknown() -> None:
    monitors = [
        make_monitor(MonitorStatus.PAUSED),
        make_monitor(MonitorStatus.PAUSED),
    ]

    status = calculate_status_page_status(monitors)

    assert status is StatusPageStatus.UNKNOWN
