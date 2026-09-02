from dataclasses import replace
from datetime import UTC, datetime

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
    ) -> None:
        self._channel = channel

    async def process(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent:
        attempts = event.attempts + 1

        try:
            await self._channel.send(event)

        except NotificationDeliveryError as exc:
            return replace(
                event,
                attempts=attempts,
                last_error=str(exc)[:2000],
            )

        return replace(
            event,
            processed_at=datetime.now(UTC),
            attempts=attempts,
            last_error=None,
        )