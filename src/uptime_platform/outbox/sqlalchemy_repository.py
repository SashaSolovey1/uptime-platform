from uuid import UUID

from sqlalchemy import select
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
            organization_id=event.organization_id,
            event_type=event.event_type,
            payload=event.payload,
            created_at=event.created_at,
            processed_at=event.processed_at,
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
    ) -> list[OutboxEvent]:
        statement = (
            select(OutboxEventModel)
            .where(OutboxEventModel.processed_at.is_(None))
            .order_by(OutboxEventModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = await self._session.execute(statement)

        return [self._to_entity(model) for model in result.scalars().all()]

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

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    @staticmethod
    def _to_entity(
        model: OutboxEventModel,
    ) -> OutboxEvent:
        return OutboxEvent(
            id=model.id,
            organization_id=model.organization_id,
            event_type=model.event_type,
            payload=model.payload,
            created_at=model.created_at,
            processed_at=model.processed_at,
        )
