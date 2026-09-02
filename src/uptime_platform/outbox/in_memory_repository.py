from uuid import UUID

from uptime_platform.outbox.entities import (
    OutboxEvent,
)


class InMemoryOutboxRepository:
    def __init__(self) -> None:
        self._events: dict[UUID, OutboxEvent] = {}

    async def create(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent:
        self._events[event.id] = event

        return event

    async def get_by_id(
        self,
        event_id: UUID,
    ) -> OutboxEvent | None:
        return self._events.get(event_id)

    async def get_pending(
        self,
        limit: int,
        max_attempts: int = 5,
    ) -> list[OutboxEvent]:
        events = [
            event
            for event in self._events.values()
            if (event.processed_at is None and event.attempts < max_attempts)
        ]

        events.sort(key=lambda event: event.created_at)

        return events[:limit]

    async def update(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent | None:
        if event.id not in self._events:
            return None

        self._events[event.id] = event

        return event
