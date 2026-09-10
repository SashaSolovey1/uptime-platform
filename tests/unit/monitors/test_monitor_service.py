from uuid import UUID, uuid4

import pytest

from uptime_platform.monitors.entities import (
    DnsMonitorConfig,
    DnsRecordType,
    HttpMethod,
    HttpMonitorConfig,
    IcmpMonitorConfig,
    MonitorStatus,
    MonitorType,
    TcpMonitorConfig,
    TlsMonitorConfig,
)
from uptime_platform.monitors.in_memory_repository import (
    InMemoryMonitorRepository,
)
from uptime_platform.monitors.schemas import (
    DnsMonitorConfigCreate,
    HttpMonitorConfigCreate,
    IcmpMonitorConfigCreate,
    MonitorCreate,
    MonitorUpdate,
    TcpMonitorConfigCreate,
    TlsMonitorConfigCreate,
)
from uptime_platform.monitors.service import MonitorService

pytestmark = pytest.mark.anyio


@pytest.fixture
def service() -> MonitorService:
    repository = InMemoryMonitorRepository()

    return MonitorService(repository)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def test_create_http_monitor(
    service: MonitorService,
) -> None:
    data = MonitorCreate(
        name="Production API",
        monitor_type=MonitorType.HTTP,
        config=HttpMonitorConfigCreate(
            url="https://example.com/health",
        ),
        interval_seconds=30,
        timeout_seconds=5,
    )

    monitor = await service.create(data)

    assert isinstance(monitor.id, UUID)
    assert monitor.name == "Production API"
    assert monitor.monitor_type is MonitorType.HTTP

    assert isinstance(
        monitor.config,
        HttpMonitorConfig,
    )

    assert monitor.config.url == "https://example.com/health"
    assert monitor.config.method is HttpMethod.GET
    assert monitor.config.expected_status_codes is None
    assert monitor.config.body_contains is None
    assert monitor.config.follow_redirects is False
    assert monitor.config.verify_tls is True

    assert monitor.interval_seconds == 30
    assert monitor.timeout_seconds == 5
    assert monitor.status is MonitorStatus.PENDING
    assert monitor.created_at.tzinfo is not None


async def test_create_http_monitor_with_custom_config(
    service: MonitorService,
) -> None:
    data = MonitorCreate(
        name="Health API",
        monitor_type=MonitorType.HTTP,
        config=HttpMonitorConfigCreate(
            url="https://example.com/health",
            method=HttpMethod.HEAD,
            expected_status_codes=[200, 204],
            follow_redirects=True,
            verify_tls=False,
        ),
        interval_seconds=30,
        timeout_seconds=5,
    )

    monitor = await service.create(data)

    assert monitor.monitor_type is MonitorType.HTTP

    assert isinstance(
        monitor.config,
        HttpMonitorConfig,
    )

    assert monitor.config.url == "https://example.com/health"
    assert monitor.config.method is HttpMethod.HEAD
    assert monitor.config.expected_status_codes == (200, 204)
    assert monitor.config.body_contains is None
    assert monitor.config.follow_redirects is True
    assert monitor.config.verify_tls is False


async def test_create_tcp_monitor(
    service: MonitorService,
) -> None:
    data = MonitorCreate(
        name="PostgreSQL",
        monitor_type=MonitorType.TCP,
        config=TcpMonitorConfigCreate(
            host="database.example.com",
            port=5432,
        ),
        interval_seconds=30,
        timeout_seconds=5,
    )

    monitor = await service.create(data)

    assert monitor.monitor_type is MonitorType.TCP

    assert isinstance(
        monitor.config,
        TcpMonitorConfig,
    )

    assert monitor.config.host == "database.example.com"
    assert monitor.config.port == 5432


async def test_create_dns_monitor(
    service: MonitorService,
) -> None:
    data = MonitorCreate(
        name="Example DNS",
        monitor_type=MonitorType.DNS,
        config=DnsMonitorConfigCreate(
            host="example.com",
            record_type=DnsRecordType.A,
        ),
        interval_seconds=30,
        timeout_seconds=5,
    )

    monitor = await service.create(data)

    assert monitor.monitor_type is MonitorType.DNS

    assert isinstance(
        monitor.config,
        DnsMonitorConfig,
    )

    assert monitor.config.host == "example.com"
    assert monitor.config.record_type is DnsRecordType.A


async def test_create_tls_monitor(
    service: MonitorService,
) -> None:
    data = MonitorCreate(
        name="Example TLS",
        monitor_type=MonitorType.TLS,
        config=TlsMonitorConfigCreate(
            host="example.com",
            port=443,
            expiry_threshold_days=14,
        ),
        interval_seconds=30,
        timeout_seconds=5,
    )

    monitor = await service.create(data)

    assert monitor.monitor_type is MonitorType.TLS

    assert isinstance(
        monitor.config,
        TlsMonitorConfig,
    )

    assert monitor.config.host == "example.com"
    assert monitor.config.port == 443
    assert monitor.config.expiry_threshold_days == 14


async def test_create_icmp_monitor(
    service: MonitorService,
) -> None:
    data = MonitorCreate(
        name="Cloudflare",
        monitor_type=MonitorType.ICMP,
        config=IcmpMonitorConfigCreate(
            host="1.1.1.1",
        ),
        interval_seconds=30,
        timeout_seconds=5,
    )

    monitor = await service.create(data)

    assert monitor.monitor_type is MonitorType.ICMP

    assert isinstance(
        monitor.config,
        IcmpMonitorConfig,
    )

    assert monitor.config.host == "1.1.1.1"


async def test_get_monitor_by_id(
    service: MonitorService,
) -> None:
    created_monitor = await service.create(
        MonitorCreate(
            name="Production API",
            monitor_type=MonitorType.HTTP,
            config=HttpMonitorConfigCreate(
                url="https://example.com/health",
            ),
        )
    )

    found_monitor = await service.get_by_id(created_monitor.id)

    assert found_monitor is not None
    assert found_monitor.id == created_monitor.id


async def test_get_nonexistent_monitor_returns_none(
    service: MonitorService,
) -> None:
    monitor = await service.get_by_id(uuid4())

    assert monitor is None


async def test_update_monitor(
    service: MonitorService,
) -> None:
    created_monitor = await service.create(
        MonitorCreate(
            name="Production API",
            monitor_type=MonitorType.HTTP,
            config=HttpMonitorConfigCreate(
                url="https://example.com/health",
            ),
            interval_seconds=30,
            timeout_seconds=5,
        )
    )

    updated_monitor = await service.update(
        created_monitor.id,
        MonitorUpdate(
            timeout_seconds=15,
        ),
    )

    assert updated_monitor is not None
    assert updated_monitor.id == created_monitor.id
    assert updated_monitor.name == "Production API"
    assert updated_monitor.interval_seconds == 30
    assert updated_monitor.timeout_seconds == 15


async def test_update_http_monitor_config(
    service: MonitorService,
) -> None:
    created_monitor = await service.create(
        MonitorCreate(
            name="Production API",
            monitor_type=MonitorType.HTTP,
            config=HttpMonitorConfigCreate(
                url="https://example.com/health",
            ),
        )
    )

    updated_monitor = await service.update(
        created_monitor.id,
        MonitorUpdate(
            config={
                "url": "https://example.org/health",
                "expected_status_codes": [200, 204],
                "body_contains": "healthy",
                "follow_redirects": True,
            },
        ),
    )

    assert updated_monitor is not None

    assert isinstance(
        updated_monitor.config,
        HttpMonitorConfig,
    )

    assert updated_monitor.config.url == "https://example.org/health"
    assert updated_monitor.config.expected_status_codes == (200, 204)
    assert updated_monitor.config.body_contains == "healthy"
    assert updated_monitor.config.follow_redirects is True


async def test_update_tls_monitor_config(
    service: MonitorService,
) -> None:
    created_monitor = await service.create(
        MonitorCreate(
            name="Example TLS",
            monitor_type=MonitorType.TLS,
            config=TlsMonitorConfigCreate(
                host="example.com",
                port=443,
                expiry_threshold_days=14,
            ),
        )
    )

    updated_monitor = await service.update(
        created_monitor.id,
        MonitorUpdate(
            config={
                "port": 8443,
                "expiry_threshold_days": 30,
            },
        ),
    )

    assert updated_monitor is not None

    assert isinstance(
        updated_monitor.config,
        TlsMonitorConfig,
    )

    assert updated_monitor.config.host == "example.com"
    assert updated_monitor.config.port == 8443
    assert updated_monitor.config.expiry_threshold_days == 30


async def test_update_icmp_monitor_config(
    service: MonitorService,
) -> None:
    created_monitor = await service.create(
        MonitorCreate(
            name="Cloudflare",
            monitor_type=MonitorType.ICMP,
            config=IcmpMonitorConfigCreate(
                host="1.1.1.1",
            ),
        )
    )

    updated_monitor = await service.update(
        created_monitor.id,
        MonitorUpdate(
            config={
                "host": "8.8.8.8",
            },
        ),
    )

    assert updated_monitor is not None

    assert isinstance(
        updated_monitor.config,
        IcmpMonitorConfig,
    )

    assert updated_monitor.config.host == "8.8.8.8"


async def test_delete_monitor(
    service: MonitorService,
) -> None:
    created_monitor = await service.create(
        MonitorCreate(
            name="Production API",
            monitor_type=MonitorType.HTTP,
            config=HttpMonitorConfigCreate(
                url="https://example.com/health",
            ),
        )
    )

    deleted = await service.delete(created_monitor.id)

    assert deleted is True

    monitor = await service.get_by_id(created_monitor.id)

    assert monitor is None
