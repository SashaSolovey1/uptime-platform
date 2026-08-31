from uptime_platform.monitors.entities import (
    MonitorStatus,
)


def status_after_check(current_status: MonitorStatus, success: bool) -> MonitorStatus:
    if current_status is MonitorStatus.PAUSED:
        return MonitorStatus.PAUSED

    if success:
        return MonitorStatus.UP

    return MonitorStatus.DOWN
