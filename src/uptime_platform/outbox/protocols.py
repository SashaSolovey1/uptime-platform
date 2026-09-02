from typing import Protocol
from uuid import UUID

from uptime_platform.outbox.entities import (
    OutboxEvent,
)


class OutboxRepositoryProtocol(Protocol):
    async def create(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent: ...

    async def get_pending(
        self,
        limit: int,
        max_attempts: int = 5,
    ) -> list[OutboxEvent]: ...

    async def update(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent | None: ...

    async def get_by_id(
        self,
        event_id: UUID,
    ) -> OutboxEvent | None: ...
