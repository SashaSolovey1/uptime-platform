from dataclasses import replace
from datetime import UTC, datetime, timedelta

from uptime_platform.notifications.exceptions import (
    NotificationDeliveryError,
)
from uptime_platform.notifications.protocols import (
    NotificationChannelProtocol,
)
from uptime_platform.outbox.entities import OutboxEvent


class NotificationService:
    def __init__(
        self,
        channel: NotificationChannelProtocol,
        retry_base_seconds: int = 5,
        retry_max_seconds: int = 300,
    ) -> None:
        self._channel = channel
        self._retry_base_seconds = retry_base_seconds
        self._retry_max_seconds = retry_max_seconds

    async def process(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent:
        attempts = event.attempts + 1

        try:
            await self._channel.send(event)

        except NotificationDeliveryError as exc:
            retry_delay = self._retry_delay(attempts)

            return replace(
                event,
                attempts=attempts,
                last_error=str(exc)[:2000],
                next_attempt_at=(datetime.now(UTC) + timedelta(seconds=retry_delay)),
                locked_until=None,
            )

        return replace(
            event,
            processed_at=datetime.now(UTC),
            attempts=attempts,
            last_error=None,
            locked_until=None,
        )

    def _retry_delay(
        self,
        attempts: int,
    ) -> int:
        delay = self._retry_base_seconds * 2 ** (attempts - 1)

        return min(
            delay,
            self._retry_max_seconds,
        )
