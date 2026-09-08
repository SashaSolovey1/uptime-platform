from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.monitors.entities import (
    DnsMonitorConfig,
    DnsRecordType,
    HttpMonitorConfig,
    Monitor,
    MonitorConfig,
    MonitorStatus,
    MonitorType,
    TcpMonitorConfig,
)
from uptime_platform.monitors.models import (
    MonitorModel,
)


class SqlAlchemyMonitorRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        monitor: Monitor,
    ) -> Monitor:
        model = MonitorModel(
            id=monitor.id,
            name=monitor.name,
            monitor_type=monitor.monitor_type,
            config=self._config_to_dict(monitor.config),
            interval_seconds=monitor.interval_seconds,
            timeout_seconds=monitor.timeout_seconds,
            status=monitor.status,
            created_at=monitor.created_at,
            next_check_at=monitor.next_check_at,
            failure_threshold=monitor.failure_threshold,
            recovery_threshold=monitor.recovery_threshold,
            consecutive_failures=monitor.consecutive_failures,
            consecutive_successes=monitor.consecutive_successes,
        )

        self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_all(
        self,
    ) -> list[Monitor]:
        result = await self._session.execute(select(MonitorModel))

        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_by_id(
        self,
        monitor_id: UUID,
    ) -> Monitor | None:
        model = await self._session.get(
            MonitorModel,
            monitor_id,
        )

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_id_for_update(
        self,
        monitor_id: UUID,
    ) -> Monitor | None:
        statement = (
            select(MonitorModel)
            .where(MonitorModel.id == monitor_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(
        self,
        monitor: Monitor,
    ) -> Monitor | None:
        model = await self._session.get(
            MonitorModel,
            monitor.id,
        )

        if model is None:
            return None

        model.name = monitor.name
        model.monitor_type = monitor.monitor_type
        model.config = self._config_to_dict(monitor.config)
        model.interval_seconds = monitor.interval_seconds
        model.timeout_seconds = monitor.timeout_seconds
        model.status = monitor.status
        model.next_check_at = monitor.next_check_at
        model.failure_threshold = monitor.failure_threshold
        model.recovery_threshold = monitor.recovery_threshold
        model.consecutive_failures = monitor.consecutive_failures
        model.consecutive_successes = monitor.consecutive_successes

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(
        self,
        monitor_id: UUID,
    ) -> bool:
        model = await self._session.get(
            MonitorModel,
            monitor_id,
        )

        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()

        return True

    async def get_due(
        self,
        now: datetime,
        limit: int,
    ) -> list[Monitor]:
        statement = (
            select(MonitorModel)
            .where(
                MonitorModel.next_check_at <= now,
                MonitorModel.status != MonitorStatus.PAUSED,
            )
            .order_by(MonitorModel.next_check_at)
            .limit(limit)
        )

        result = await self._session.execute(statement)

        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    @staticmethod
    def _config_to_dict(
        config: MonitorConfig,
    ) -> dict[str, object]:
        if isinstance(
            config,
            HttpMonitorConfig,
        ):
            return {
                "url": config.url,
            }

        if isinstance(
            config,
            TcpMonitorConfig,
        ):
            return {
                "host": config.host,
                "port": config.port,
            }

        if isinstance(
            config,
            DnsMonitorConfig,
        ):
            return {
                "host": config.host,
                "record_type": config.record_type.value,
            }

        raise TypeError(f"Unsupported monitor config: {type(config)}")

    @staticmethod
    def _to_entity(
        model: MonitorModel,
    ) -> Monitor:
        if model.monitor_type is MonitorType.HTTP:
            config = HttpMonitorConfig(
                url=str(model.config["url"]),
            )

        elif model.monitor_type is MonitorType.TCP:
            config = TcpMonitorConfig(
                host=str(model.config["host"]),
                port=int(model.config["port"]),
            )

        elif model.monitor_type is MonitorType.DNS:
            config = DnsMonitorConfig(
                host=str(model.config["host"]),
                record_type=DnsRecordType(str(model.config["record_type"])),
            )

        else:
            raise ValueError(f"Unsupported monitor type: {model.monitor_type}")

        return Monitor(
            id=model.id,
            name=model.name,
            monitor_type=model.monitor_type,
            config=config,
            interval_seconds=model.interval_seconds,
            timeout_seconds=model.timeout_seconds,
            status=model.status,
            created_at=model.created_at,
            next_check_at=model.next_check_at,
            failure_threshold=model.failure_threshold,
            recovery_threshold=model.recovery_threshold,
            consecutive_failures=model.consecutive_failures,
            consecutive_successes=model.consecutive_successes,
        )
