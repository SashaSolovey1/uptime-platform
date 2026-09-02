from typing import Protocol

from uptime_platform.outbox.entities import OutboxEvent


class NotificationChannelProtocol(Protocol):
    async def send(
        self,
        event: OutboxEvent,
    ) -> None: ...
