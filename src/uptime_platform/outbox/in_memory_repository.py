from dataclasses import replace
from datetime import datetime
from uuid import UUID

from uptime_platform.outbox.entities import OutboxEvent


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

    async def claim_pending(
        self,
        limit: int,
        max_attempts: int,
        now: datetime,
        locked_until: datetime,
    ) -> list[OutboxEvent]:
        events = [
            event
            for event in self._events.values()
            if (
                event.processed_at is None
                and event.attempts < max_attempts
                and event.next_attempt_at <= now
                and (event.locked_until is None or event.locked_until <= now)
            )
        ]

        events.sort(key=lambda event: event.created_at)

        events = events[:limit]

        claimed: list[OutboxEvent] = []

        for event in events:
            claimed_event = replace(
                event,
                locked_until=locked_until,
            )

            self._events[event.id] = claimed_event
            claimed.append(claimed_event)

        return claimed

    async def update(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent | None:
        if event.id not in self._events:
            return None

        self._events[event.id] = event

        return event
