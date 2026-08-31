import pytest

from uptime_platform.monitors.entities import MonitorStatus
from uptime_platform.monitors.state import status_after_check


@pytest.mark.parametrize(
    ("current_status", "success", "expected_status"),
    [
        (
            MonitorStatus.PENDING,
            True,
            MonitorStatus.UP,
        ),
        (
            MonitorStatus.PENDING,
            False,
            MonitorStatus.DOWN,
        ),
        (
            MonitorStatus.UP,
            True,
            MonitorStatus.UP,
        ),
        (
            MonitorStatus.UP,
            False,
            MonitorStatus.DOWN,
        ),
        (
            MonitorStatus.DOWN,
            True,
            MonitorStatus.UP,
        ),
        (
            MonitorStatus.DOWN,
            False,
            MonitorStatus.DOWN,
        ),
        (
            MonitorStatus.PAUSED,
            True,
            MonitorStatus.PAUSED,
        ),
        (
            MonitorStatus.PAUSED,
            False,
            MonitorStatus.PAUSED,
        ),
    ],
)
def test_status_after_check(
    current_status: MonitorStatus,
    success: bool,
    expected_status: MonitorStatus,
) -> None:
    result = status_after_check(
        current_status=current_status,
        success=success,
    )

    assert result is expected_status
