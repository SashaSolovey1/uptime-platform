import asyncio
import logging
from datetime import UTC, datetime, timedelta

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
        lease_seconds: int = 60,
    ) -> None:
        self._session_factory = session_factory
        self._poll_interval_seconds = poll_interval_seconds
        self._batch_size = batch_size
        self._max_attempts = max_attempts
        self._lease_seconds = lease_seconds

        self._semaphore = asyncio.Semaphore(concurrency)

        self._service = NotificationService(channel)

    async def run_forever(self) -> None:
        while True:
            try:
                processed = await self.run_once()

                if processed > 0:
                    logger.info(
                        "notification worker claimed %d event(s)",
                        processed,
                    )

            except Exception:
                logger.exception("notification worker iteration failed")

            await asyncio.sleep(self._poll_interval_seconds)

    async def run_once(self) -> int:
        events = await self._claim_events()

        if not events:
            return 0

        await asyncio.gather(*[self._process_event(event) for event in events])

        return len(events)

    async def _claim_events(
        self,
    ) -> list[OutboxEvent]:
        now = datetime.now(UTC)

        locked_until = now + timedelta(seconds=self._lease_seconds)

        async with self._session_factory() as session:
            try:
                repository = SqlAlchemyOutboxRepository(session)

                events = await repository.claim_pending(
                    limit=self._batch_size,
                    max_attempts=self._max_attempts,
                    now=now,
                    locked_until=locked_until,
                )

                await session.commit()

                return events

            except Exception:
                await session.rollback()
                raise

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
