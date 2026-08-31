from dataclasses import replace

from uptime_platform.monitors.entities import (
    Monitor,
    MonitorStatus,
)


def apply_check_result(
    monitor: Monitor,
    success: bool,
) -> Monitor:
    if monitor.status is MonitorStatus.PAUSED:
        return monitor

    if success:
        consecutive_successes = monitor.consecutive_successes + 1

        if monitor.status is MonitorStatus.PENDING or (
            monitor.status is MonitorStatus.DOWN
            and consecutive_successes >= monitor.recovery_threshold
        ):
            new_status = MonitorStatus.UP

        else:
            new_status = monitor.status

        return replace(
            monitor,
            status=new_status,
            consecutive_failures=0,
            consecutive_successes=consecutive_successes,
        )

    consecutive_failures = monitor.consecutive_failures + 1

    if consecutive_failures >= monitor.failure_threshold:
        new_status = MonitorStatus.DOWN
    else:
        new_status = monitor.status

    return replace(
        monitor,
        status=new_status,
        consecutive_failures=consecutive_failures,
        consecutive_successes=0,
    )
