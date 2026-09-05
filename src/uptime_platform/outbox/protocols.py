from typing import Protocol
from uuid import UUID

from uptime_platform.outbox.entities import OutboxEvent


class OutboxRepositoryProtocol(Protocol):
    async def create(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent: ...

    async def get_by_id(
        self,
        event_id: UUID,
    ) -> OutboxEvent | None: ...

    async def claim_pending(
        self,
        limit: int,
    ) -> list[OutboxEvent]: ...

    async def update(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent | None: ...
