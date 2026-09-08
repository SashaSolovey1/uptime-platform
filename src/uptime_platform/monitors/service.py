from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from uptime_platform.monitors.entities import (
    DnsMonitorConfig,
    HttpMonitorConfig,
    Monitor,
    MonitorConfig,
    MonitorStatus,
    TcpMonitorConfig,
)
from uptime_platform.monitors.protocols import (
    MonitorRepositoryProtocol,
)
from uptime_platform.monitors.schemas import (
    DnsMonitorConfigCreate,
    DnsMonitorConfigUpdate,
    HttpMonitorConfigCreate,
    HttpMonitorConfigUpdate,
    MonitorCreate,
    MonitorUpdate,
    TcpMonitorConfigCreate,
    TcpMonitorConfigUpdate,
)


def _create_config(
    config: (HttpMonitorConfigCreate | TcpMonitorConfigCreate),
) -> MonitorConfig:
    if isinstance(
        config,
        HttpMonitorConfigCreate,
    ):
        return HttpMonitorConfig(
            url=str(config.url),
        )

    if isinstance(
        config,
        TcpMonitorConfigCreate,
    ):
        return TcpMonitorConfig(
            host=config.host,
            port=config.port,
        )

    if isinstance(
        config,
        DnsMonitorConfigCreate,
    ):
        return DnsMonitorConfig(
            host=config.host,
            record_type=config.record_type,
        )

    raise TypeError(f"Unsupported monitor config: {type(config)}")


def _update_config(
    current: MonitorConfig,
    update: (HttpMonitorConfigUpdate | TcpMonitorConfigUpdate),
) -> MonitorConfig:

    if not update.model_fields_set:
        return current

    if isinstance(current, HttpMonitorConfig) and isinstance(
        update,
        HttpMonitorConfigUpdate,
    ):
        return HttpMonitorConfig(
            url=(str(update.url) if update.url is not None else current.url),
        )

    if isinstance(current, TcpMonitorConfig) and isinstance(
        update,
        TcpMonitorConfigUpdate,
    ):
        return TcpMonitorConfig(
            host=(update.host if update.host is not None else current.host),
            port=(update.port if update.port is not None else current.port),
        )

    if isinstance(current, DnsMonitorConfig) and isinstance(
        update,
        DnsMonitorConfigUpdate,
    ):
        return DnsMonitorConfig(
            host=(update.host if update.host is not None else current.host),
            record_type=(
                update.record_type
                if update.record_type is not None
                else current.record_type
            ),
        )

    raise ValueError("Monitor config type does not match monitor type")


class MonitorService:
    def __init__(
        self,
        repository: MonitorRepositoryProtocol,
    ) -> None:
        self._repository = repository

    async def create(
        self,
        data: MonitorCreate,
    ) -> Monitor:
        now = datetime.now(UTC)

        monitor = Monitor(
            id=uuid4(),
            name=data.name,
            monitor_type=data.monitor_type,
            config=_create_config(data.config),
            interval_seconds=data.interval_seconds,
            timeout_seconds=data.timeout_seconds,
            status=MonitorStatus.PENDING,
            created_at=now,
            next_check_at=now,
            failure_threshold=data.failure_threshold,
            recovery_threshold=data.recovery_threshold,
        )

        return await self._repository.create(monitor)

    async def get_all(
        self,
    ) -> list[Monitor]:
        return await self._repository.get_all()

    async def get_by_id(
        self,
        monitor_id: UUID,
    ) -> Monitor | None:
        return await self._repository.get_by_id(monitor_id)

    async def update(
        self,
        monitor_id: UUID,
        data: MonitorUpdate,
    ) -> Monitor | None:
        monitor = await self._repository.get_by_id(monitor_id)

        if monitor is None:
            return None

        config = monitor.config

        if data.config is not None:
            config = _update_config(
                current=monitor.config,
                update=data.config,
            )

        updated_monitor = replace(
            monitor,
            name=(data.name if data.name is not None else monitor.name),
            config=config,
            interval_seconds=(
                data.interval_seconds
                if data.interval_seconds is not None
                else monitor.interval_seconds
            ),
            timeout_seconds=(
                data.timeout_seconds
                if data.timeout_seconds is not None
                else monitor.timeout_seconds
            ),
            failure_threshold=(
                data.failure_threshold
                if data.failure_threshold is not None
                else monitor.failure_threshold
            ),
            recovery_threshold=(
                data.recovery_threshold
                if data.recovery_threshold is not None
                else monitor.recovery_threshold
            ),
        )

        return await self._repository.update(updated_monitor)

    async def delete(
        self,
        monitor_id: UUID,
    ) -> bool:
        return await self._repository.delete(monitor_id)
