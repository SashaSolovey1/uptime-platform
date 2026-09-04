from datetime import UTC, datetime, timedelta
from uuid import uuid4

from uptime_platform.maintenance.entities import (
    MaintenanceWindow,
)


def test_maintenance_window_is_active() -> None:
    now = datetime.now(UTC)

    window = MaintenanceWindow(
        id=uuid4(),
        monitor_id=uuid4(),
        starts_at=now - timedelta(minutes=5),
        ends_at=now + timedelta(minutes=5),
        reason="Deployment",
        created_at=now,
    )

    assert window.is_active(now) is True


def test_maintenance_window_is_not_active_before_start() -> None:
    now = datetime.now(UTC)

    window = MaintenanceWindow(
        id=uuid4(),
        monitor_id=uuid4(),
        starts_at=now + timedelta(minutes=5),
        ends_at=now + timedelta(minutes=10),
        reason=None,
        created_at=now,
    )

    assert window.is_active(now) is False
