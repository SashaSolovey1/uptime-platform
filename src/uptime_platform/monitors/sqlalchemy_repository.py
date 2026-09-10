from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.monitors.entities import (
    DnsMonitorConfig,
    DnsRecordType,
    HttpMethod,
    HttpMonitorConfig,
    IcmpMonitorConfig,
    Monitor,
    MonitorConfig,
    MonitorStatus,
    MonitorType,
    TcpMonitorConfig,
    TlsMonitorConfig,
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
                "method": config.method.value,
                "expected_status_codes": (
                    list(config.expected_status_codes)
                    if config.expected_status_codes is not None
                    else None
                ),
                "body_contains": config.body_contains,
                "follow_redirects": config.follow_redirects,
                "verify_tls": config.verify_tls,
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

        if isinstance(
            config,
            TlsMonitorConfig,
        ):
            return {
                "host": config.host,
                "port": config.port,
                "expiry_threshold_days": config.expiry_threshold_days,
            }

        if isinstance(
            config,
            IcmpMonitorConfig,
        ):
            return {
                "host": config.host,
            }

        raise TypeError(f"Unsupported monitor config: {type(config)}")

    @staticmethod
    def _to_entity(
        model: MonitorModel,
    ) -> Monitor:
        if model.monitor_type is MonitorType.HTTP:
            raw_status_codes = model.config.get("expected_status_codes")

            config = HttpMonitorConfig(
                url=str(model.config["url"]),
                method=HttpMethod(
                    str(
                        model.config.get(
                            "method",
                            HttpMethod.GET.value,
                        )
                    )
                ),
                expected_status_codes=(
                    tuple(int(status_code) for status_code in raw_status_codes)
                    if raw_status_codes is not None
                    else None
                ),
                body_contains=(
                    str(model.config["body_contains"])
                    if model.config.get("body_contains") is not None
                    else None
                ),
                follow_redirects=bool(
                    model.config.get(
                        "follow_redirects",
                        False,
                    )
                ),
                verify_tls=bool(
                    model.config.get(
                        "verify_tls",
                        True,
                    )
                ),
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

        elif model.monitor_type is MonitorType.TLS:
            config = TlsMonitorConfig(
                host=str(model.config["host"]),
                port=int(
                    model.config.get(
                        "port",
                        443,
                    )
                ),
                expiry_threshold_days=int(
                    model.config.get(
                        "expiry_threshold_days",
                        14,
                    )
                ),
            )

        elif model.monitor_type is MonitorType.ICMP:
            config = IcmpMonitorConfig(
                host=str(model.config["host"]),
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
