import asyncio
import logging
from datetime import UTC, datetime, timedelta

import httpx2
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from uptime_platform.notifications.entities import (
    NotificationDelivery,
)
from uptime_platform.notifications.factory import (
    create_notification_channel,
)
from uptime_platform.notifications.service import (
    NotificationFanoutService,
    NotificationService,
)
from uptime_platform.notifications.sqlalchemy_repository import (
    SqlAlchemyNotificationDeliveryRepository,
    SqlAlchemyNotificationDestinationRepository,
)
from uptime_platform.outbox.sqlalchemy_repository import (
    SqlAlchemyOutboxRepository,
)

logger = logging.getLogger(__name__)


class NotificationWorker:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        http_client: httpx2.AsyncClient,
        poll_interval_seconds: int = 5,
        batch_size: int = 100,
        concurrency: int = 10,
        max_attempts: int = 5,
        lease_seconds: int = 60,
        notification_timeout_seconds: float = 5,
    ) -> None:
        self._session_factory = session_factory
        self._http_client = http_client

        self._poll_interval_seconds = poll_interval_seconds
        self._batch_size = batch_size
        self._max_attempts = max_attempts
        self._lease_seconds = lease_seconds
        self._notification_timeout_seconds = notification_timeout_seconds

        self._semaphore = asyncio.Semaphore(concurrency)

        self._notification_service = NotificationService()

    async def run_forever(self) -> None:
        while True:
            try:
                fanout_count, delivery_count = await self.run_once()

                if fanout_count > 0 or delivery_count > 0:
                    logger.info(
                        "notification worker fanout=%d deliveries=%d",
                        fanout_count,
                        delivery_count,
                    )

            except Exception:
                logger.exception("notification worker iteration failed")

            await asyncio.sleep(self._poll_interval_seconds)

    async def run_once(
        self,
    ) -> tuple[int, int]:
        fanout_count = await self._fan_out_pending_events()

        deliveries = await self._claim_deliveries()

        if deliveries:
            await asyncio.gather(
                *[self._process_delivery_safely(delivery) for delivery in deliveries]
            )

        return (
            fanout_count,
            len(deliveries),
        )

    async def _claim_deliveries(
        self,
    ) -> list[NotificationDelivery]:
        now = datetime.now(UTC)

        locked_until = now + timedelta(seconds=self._lease_seconds)

        async with self._session_factory() as session:
            repository = SqlAlchemyNotificationDeliveryRepository(session)

            async with session.begin():
                return await repository.claim_pending(
                    limit=self._batch_size,
                    max_attempts=self._max_attempts,
                    now=now,
                    locked_until=locked_until,
                )

    async def _process_delivery_safely(
        self,
        delivery: NotificationDelivery,
    ) -> None:
        try:
            await self._process_delivery(delivery)

        except Exception:
            logger.exception(
                "notification delivery failed delivery_id=%s",
                delivery.id,
            )

    async def _process_delivery(
        self,
        delivery: NotificationDelivery,
    ) -> None:
        async with self._semaphore:
            (
                event,
                destination,
            ) = await self._load_delivery_data(delivery)

            if event is None:
                logger.warning(
                    "outbox event not found delivery_id=%s event_id=%s",
                    delivery.id,
                    delivery.event_id,
                )

                return

            if destination is None:
                logger.warning(
                    "notification destination not found "
                    "delivery_id=%s destination_id=%s",
                    delivery.id,
                    delivery.destination_id,
                )

                return

            channel = create_notification_channel(
                destination=destination,
                client=self._http_client,
                timeout_seconds=self._notification_timeout_seconds,
            )

            updated_delivery = await self._notification_service.process(
                delivery=delivery,
                event=event,
                channel=channel,
            )

            async with self._session_factory() as session, session.begin():
                repository = SqlAlchemyNotificationDeliveryRepository(session)

                await repository.update(updated_delivery)

    async def _load_delivery_data(
        self,
        delivery: NotificationDelivery,
    ):
        async with self._session_factory() as session:
            outbox_repository = SqlAlchemyOutboxRepository(session)

            destination_repository = SqlAlchemyNotificationDestinationRepository(
                session
            )

            event = await outbox_repository.get_by_id(delivery.event_id)

            destination = await destination_repository.get_by_id(
                delivery.destination_id
            )

            return event, destination

    async def _fan_out_pending_events(
        self,
    ) -> int:
        async with self._session_factory() as session, session.begin():
            outbox_repository = SqlAlchemyOutboxRepository(session)

            destination_repository = SqlAlchemyNotificationDestinationRepository(
                session
            )

            delivery_repository = SqlAlchemyNotificationDeliveryRepository(session)

            events = await outbox_repository.claim_pending(limit=self._batch_size)

            service = NotificationFanoutService(
                destination_repository=destination_repository,
                delivery_repository=delivery_repository,
                outbox_repository=outbox_repository,
            )

            for event in events:
                await service.fan_out(event)

            return len(events)
