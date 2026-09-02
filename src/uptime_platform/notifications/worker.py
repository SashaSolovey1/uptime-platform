import asyncio
import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from uptime_platform.notifications.protocols import (
    NotificationChannelProtocol,
)
from uptime_platform.notifications.service import (
    NotificationService,
)
from uptime_platform.outbox.entities import OutboxEvent
from uptime_platform.outbox.sqlalchemy_repository import (
    SqlAlchemyOutboxRepository,
)

logger = logging.getLogger(__name__)


class NotificationWorker:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        channel: NotificationChannelProtocol,
        poll_interval_seconds: int = 5,
        batch_size: int = 100,
        concurrency: int = 10,
        max_attempts: int = 5,
    ) -> None:
        self._session_factory = session_factory
        self._poll_interval_seconds = poll_interval_seconds
        self._batch_size = batch_size
        self._max_attempts = max_attempts

        self._semaphore = asyncio.Semaphore(concurrency)

        self._service = NotificationService(channel)

    async def run_forever(self) -> None:
        while True:
            try:
                await self.run_once()

            except Exception:
                logger.exception("notification worker iteration failed")

            await asyncio.sleep(self._poll_interval_seconds)

    async def run_once(self) -> int:
        events = await self._get_pending_events()

        if not events:
            return 0

        await asyncio.gather(*[self._process_event(event) for event in events])

        return len(events)

    async def _get_pending_events(
        self,
    ) -> list[OutboxEvent]:
        async with self._session_factory() as session:
            repository = SqlAlchemyOutboxRepository(session)

            return await repository.get_pending(
                limit=self._batch_size,
                max_attempts=self._max_attempts,
            )

    async def _process_event(
        self,
        event: OutboxEvent,
    ) -> None:
        async with self._semaphore:
            updated_event = await self._service.process(event)

            async with self._session_factory() as session:
                try:
                    repository = SqlAlchemyOutboxRepository(session)

                    await repository.update(updated_event)

                    await session.commit()

                except Exception:
                    await session.rollback()
                    raise
