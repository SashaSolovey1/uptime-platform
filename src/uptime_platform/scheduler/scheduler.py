import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from uptime_platform.checks.http import HttpChecker
from uptime_platform.checks.service import CheckService
from uptime_platform.checks.sqlalchemy_repository import (
    SqlAlchemyCheckRepository,
)
from uptime_platform.incidents.sqlalchemy_repository import (
    SqlAlchemyIncidentRepository,
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
    ) -> None:
        self._session_factory = session_factory
        self._poll_interval_seconds = poll_interval_seconds
        self._batch_size = batch_size

        self._semaphore = asyncio.Semaphore(concurrency)

        self._checker = HttpChecker()

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
            result = await self._checker.check(
                url=monitor.url,
                timeout_seconds=monitor.timeout_seconds,
            )

            async with self._session_factory() as session:
                try:
                    monitor_repository = SqlAlchemyMonitorRepository(session)

                    check_repository = SqlAlchemyCheckRepository(session)

                    incident_repository = SqlAlchemyIncidentRepository(session)

                    outbox_repository = SqlAlchemyOutboxRepository(session)

                    service = CheckService(
                        monitor_repository=monitor_repository,
                        check_repository=check_repository,
                        incident_repository=incident_repository,
                        outbox_repository=outbox_repository,
                        checker=self._checker,
                    )

                    await service.record(
                        monitor_id=monitor.id,
                        result=result,
                    )

                    await session.commit()

                except Exception:
                    await session.rollback()
                    raise
