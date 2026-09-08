from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.monitors.entities import (
    DnsMonitorConfig,
    DnsRecordType,
    HttpMonitorConfig,
    Monitor,
    MonitorStatus,
    MonitorType,
    TcpMonitorConfig,
)
from uptime_platform.monitors.models import MonitorModel
from uptime_platform.monitors.sqlalchemy_repository import (
    SqlAlchemyMonitorRepository,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository(db_session: AsyncSession) -> SqlAlchemyMonitorRepository:
    return SqlAlchemyMonitorRepository(db_session)


def make_monitor(
    status: MonitorStatus = MonitorStatus.PENDING,
) -> Monitor:
    now = datetime.now(UTC)

    return Monitor(
        id=uuid4(),
        name="Production API",
        monitor_type=MonitorType.HTTP,
        config=HttpMonitorConfig(
            url="https://example.com/health",
        ),
        interval_seconds=30,
        timeout_seconds=5,
        status=status,
        created_at=now,
        next_check_at=now,
    )


async def test_create_monitor(
    repository: SqlAlchemyMonitorRepository,
    db_session: AsyncSession,
) -> None:
    monitor = make_monitor()

    created_monitor = await repository.create(monitor)

    db_session.expunge_all()

    model = await db_session.get(
        MonitorModel,
        monitor.id,
    )

    assert created_monitor == monitor

    assert model is not None
    assert model.id == monitor.id
    assert model.name == monitor.name


async def test_get_monitor_by_id(
    repository: SqlAlchemyMonitorRepository,
    db_session: AsyncSession,
) -> None:
    monitor_id = uuid4()

    now = datetime.now(UTC)

    model = MonitorModel(
        id=monitor_id,
        name="Production API",
        monitor_type=MonitorType.HTTP,
        config={
            "url": "https://example.com/health",
        },
        interval_seconds=30,
        timeout_seconds=5,
        status=MonitorStatus.PENDING,
        created_at=now,
        next_check_at=now,
    )

    db_session.add(model)
    await db_session.commit()

    db_session.expunge_all()

    monitor = await repository.get_by_id(monitor_id)

    assert monitor is not None
    assert monitor.id == monitor_id
    assert monitor.name == "Production API"

    assert monitor.monitor_type is MonitorType.HTTP

    assert isinstance(
        monitor.config,
        HttpMonitorConfig,
    )

    assert monitor.config.url == "https://example.com/health"

    assert monitor.interval_seconds == 30
    assert monitor.timeout_seconds == 5
    assert monitor.status == MonitorStatus.PENDING


async def test_get_nonexistent_monitor_returns_none(
    repository: SqlAlchemyMonitorRepository,
) -> None:
    monitor = await repository.get_by_id(uuid4())

    assert monitor is None


async def test_update_monitor(
    repository: SqlAlchemyMonitorRepository,
) -> None:
    monitor = make_monitor()

    await repository.create(monitor)

    updated_monitor = replace(
        monitor,
        name="Updated API",
        timeout_seconds=15,
    )

    result = await repository.update(updated_monitor)

    assert result is not None
    assert result.name == "Updated API"
    assert result.timeout_seconds == 15

    found_monitor = await repository.get_by_id(monitor.id)

    assert found_monitor is not None
    assert found_monitor.name == "Updated API"
    assert found_monitor.timeout_seconds == 15


async def test_delete_monitor(
    repository: SqlAlchemyMonitorRepository,
) -> None:
    monitor = make_monitor()

    await repository.create(monitor)

    deleted = await repository.delete(monitor.id)

    assert deleted is True

    found_monitor = await repository.get_by_id(monitor.id)

    assert found_monitor is None


async def test_get_all_monitors(
    repository: SqlAlchemyMonitorRepository,
) -> None:
    first = make_monitor()

    second = replace(
        make_monitor(),
        name="Website",
        config=HttpMonitorConfig(
            url="https://example.org",
        ),
    )

    await repository.create(first)
    await repository.create(second)

    monitors = await repository.get_all()

    assert len(monitors) == 2

    ids = {monitor.id for monitor in monitors}

    assert ids == {
        first.id,
        second.id,
    }


async def test_tcp_monitor_round_trip(
    repository: SqlAlchemyMonitorRepository,
    db_session: AsyncSession,
) -> None:
    now = datetime.now(UTC)

    monitor = Monitor(
        id=uuid4(),
        name="PostgreSQL",
        monitor_type=MonitorType.TCP,
        config=TcpMonitorConfig(
            host="database.example.com",
            port=5432,
        ),
        interval_seconds=30,
        timeout_seconds=5,
        status=MonitorStatus.PENDING,
        created_at=now,
        next_check_at=now,
    )

    await repository.create(monitor)

    db_session.expunge_all()

    model = await db_session.get(
        MonitorModel,
        monitor.id,
    )

    assert model is not None
    assert model.monitor_type is MonitorType.TCP

    assert model.config == {
        "host": "database.example.com",
        "port": 5432,
    }

    found_monitor = await repository.get_by_id(monitor.id)

    assert found_monitor is not None
    assert found_monitor.monitor_type is MonitorType.TCP

    assert isinstance(
        found_monitor.config,
        TcpMonitorConfig,
    )

    assert found_monitor.config.host == "database.example.com"
    assert found_monitor.config.port == 5432


async def test_dns_monitor_round_trip(
    repository: SqlAlchemyMonitorRepository,
    db_session: AsyncSession,
) -> None:
    now = datetime.now(UTC)

    monitor = Monitor(
        id=uuid4(),
        name="Example DNS",
        monitor_type=MonitorType.DNS,
        config=DnsMonitorConfig(
            host="example.com",
            record_type=DnsRecordType.A,
        ),
        interval_seconds=30,
        timeout_seconds=5,
        status=MonitorStatus.PENDING,
        created_at=now,
        next_check_at=now,
    )

    await repository.create(monitor)

    db_session.expunge_all()

    model = await db_session.get(
        MonitorModel,
        monitor.id,
    )

    assert model is not None
    assert model.monitor_type is MonitorType.DNS

    assert model.config == {
        "host": "example.com",
        "record_type": "A",
    }

    found_monitor = await repository.get_by_id(monitor.id)

    assert found_monitor is not None
    assert found_monitor.monitor_type is MonitorType.DNS

    assert isinstance(
        found_monitor.config,
        DnsMonitorConfig,
    )

    assert found_monitor.config.host == "example.com"
    assert found_monitor.config.record_type is DnsRecordType.A
