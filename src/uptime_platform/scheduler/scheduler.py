import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from uptime_platform.checks.factory import (
    CheckerFactory,
)
from uptime_platform.checks.protocols import (
    CheckerFactoryProtocol,
)
from uptime_platform.checks.service import CheckService
from uptime_platform.checks.sqlalchemy_repository import (
    SqlAlchemyCheckRepository,
)
from uptime_platform.incidents.sqlalchemy_repository import (
    SqlAlchemyIncidentRepository,
)
from uptime_platform.maintenance.sqlalchemy_repository import (
    SqlAlchemyMaintenanceWindowRepository,
)
from uptime_platform.monitors.entities import Monitor
from uptime_platform.monitors.sqlalchemy_repository import (
    SqlAlchemyMonitorRepository,
)
from uptime_platform.outbox.sqlalchemy_repository import (
    SqlAlchemyOutboxRepository,
)

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        poll_interval_seconds: int = 1,
        batch_size: int = 100,
        concurrency: int = 20,
        checker_factory: CheckerFactoryProtocol | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._poll_interval_seconds = poll_interval_seconds
        self._batch_size = batch_size

        self._semaphore = asyncio.Semaphore(concurrency)

        self._checker_factory = (
            checker_factory if checker_factory is not None else CheckerFactory()
        )

    async def run_forever(self) -> None:
        while True:
            processed = await self.run_once()

            if processed > 0:
                logger.info(
                    "scheduler processed %d monitor(s)",
                    processed,
                )

            await asyncio.sleep(self._poll_interval_seconds)

    async def run_once(self) -> int:
        monitors = await self._get_due_monitors()

        if not monitors:
            return 0

        await asyncio.gather(*[self._check_monitor(monitor) for monitor in monitors])

        return len(monitors)

    async def _get_due_monitors(
        self,
    ) -> list[Monitor]:
        async with self._session_factory() as session:
            repository = SqlAlchemyMonitorRepository(session)

            return await repository.get_due(
                now=datetime.now(UTC),
                limit=self._batch_size,
            )

    async def _check_monitor(
        self,
        monitor: Monitor,
    ) -> None:
        async with self._semaphore:
            checker = self._checker_factory.create(monitor)

            result = await checker.check(
                timeout_seconds=(monitor.timeout_seconds),
            )

            async with self._session_factory() as session:
                try:
                    monitor_repository = SqlAlchemyMonitorRepository(session)

                    check_repository = SqlAlchemyCheckRepository(session)

                    incident_repository = SqlAlchemyIncidentRepository(session)

                    outbox_repository = SqlAlchemyOutboxRepository(session)

                    maintenance_repository = SqlAlchemyMaintenanceWindowRepository(
                        session
                    )

                    service = CheckService(
                        monitor_repository=(monitor_repository),
                        check_repository=(check_repository),
                        incident_repository=(incident_repository),
                        outbox_repository=(outbox_repository),
                        maintenance_repository=(maintenance_repository),
                        checker_factory=(self._checker_factory),
                    )

                    await service.record(
                        monitor_id=monitor.id,
                        result=result,
                    )

                    await session.commit()

                except Exception:
                    await session.rollback()
                    raise
