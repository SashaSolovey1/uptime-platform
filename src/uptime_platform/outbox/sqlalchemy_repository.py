from datetime import datetime
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.outbox.entities import (
    OutboxEvent,
)
from uptime_platform.outbox.models import (
    OutboxEventModel,
)


class SqlAlchemyOutboxRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent:
        model = OutboxEventModel(
            id=event.id,
            event_type=event.event_type,
            payload=event.payload,
            created_at=event.created_at,
            processed_at=event.processed_at,
            attempts=event.attempts,
            last_error=event.last_error,
            next_attempt_at=event.next_attempt_at,
            locked_until=event.locked_until,
        )

        self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(
        self,
        event_id: UUID,
    ) -> OutboxEvent | None:
        model = await self._session.get(
            OutboxEventModel,
            event_id,
        )

        if model is None:
            return None

        return self._to_entity(model)

    async def claim_pending(
        self,
        limit: int,
        max_attempts: int,
        now: datetime,
        locked_until: datetime,
    ) -> list[OutboxEvent]:
        statement = (
            select(OutboxEventModel)
            .where(
                OutboxEventModel.processed_at.is_(None),
                OutboxEventModel.attempts < max_attempts,
                OutboxEventModel.next_attempt_at <= now,
                or_(
                    OutboxEventModel.locked_until.is_(None),
                    OutboxEventModel.locked_until <= now,
                ),
            )
            .order_by(OutboxEventModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = await self._session.execute(statement)

        models = result.scalars().all()

        for model in models:
            model.locked_until = locked_until

        await self._session.flush()

        return [self._to_entity(model) for model in models]

    async def update(
        self,
        event: OutboxEvent,
    ) -> OutboxEvent | None:
        model = await self._session.get(
            OutboxEventModel,
            event.id,
        )

        if model is None:
            return None

        model.processed_at = event.processed_at
        model.attempts = event.attempts
        model.last_error = event.last_error
        model.next_attempt_at = event.next_attempt_at
        model.locked_until = event.locked_until

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    @staticmethod
    def _to_entity(
        model: OutboxEventModel,
    ) -> OutboxEvent:
        return OutboxEvent(
            id=model.id,
            event_type=model.event_type,
            payload=model.payload,
            created_at=model.created_at,
            processed_at=model.processed_at,
            attempts=model.attempts,
            last_error=model.last_error,
            next_attempt_at=model.next_attempt_at,
            locked_until=model.locked_until,
        )
