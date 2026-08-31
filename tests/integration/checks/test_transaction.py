from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.checks.entities import CheckResult
from uptime_platform.checks.models import CheckModel
from uptime_platform.checks.sqlalchemy_repository import (
    SqlAlchemyCheckRepository,
)
from uptime_platform.monitors.entities import MonitorStatus
from uptime_platform.monitors.models import MonitorModel
from uptime_platform.monitors.sqlalchemy_repository import (
    SqlAlchemyMonitorRepository,
)

pytestmark = pytest.mark.anyio


async def test_check_and_monitor_update_can_be_rolled_back(
    db_session: AsyncSession,
) -> None:
    monitor_id = uuid4()

    model = MonitorModel(
        id=monitor_id,
        name="Production API",
        url="https://example.com",
        interval_seconds=60,
        timeout_seconds=5,
        status=MonitorStatus.PENDING,
        created_at=datetime.now(UTC),
    )

    db_session.add(model)
    await db_session.commit()

    monitor_repository = SqlAlchemyMonitorRepository(db_session)
    check_repository = SqlAlchemyCheckRepository(db_session)

    monitor = await monitor_repository.get_by_id(monitor_id)

    assert monitor is not None

    await check_repository.create(
        monitor_id=monitor_id,
        result=CheckResult(
            success=True,
            response_time_ms=42.0,
            status_code=200,
            error=None,
        ),
    )

    await monitor_repository.update(
        replace(
            monitor,
            status=MonitorStatus.UP,
        )
    )

    await db_session.rollback()

    db_session.expunge_all()

    persisted_monitor = await db_session.get(
        MonitorModel,
        monitor_id,
    )

    checks_result = await db_session.execute(
        select(CheckModel).where(CheckModel.monitor_id == monitor_id)
    )

    checks = checks_result.scalars().all()

    assert persisted_monitor is not None
    assert persisted_monitor.status is MonitorStatus.PENDING
    assert checks == []
