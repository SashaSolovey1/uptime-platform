from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.notifications.entities import (
    NotificationDestination,
)
from uptime_platform.notifications.models import (
    NotificationDestinationModel,
)


class SqlAlchemyNotificationDestinationRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        destination: NotificationDestination,
    ) -> NotificationDestination:
        model = NotificationDestinationModel(
            id=destination.id,
            name=destination.name,
            destination_type=destination.destination_type,
            enabled=destination.enabled,
            webhook_url=destination.webhook_url,
            webhook_secret=destination.webhook_secret,
            created_at=destination.created_at,
        )

        self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(
        self,
        destination_id: UUID,
    ) -> NotificationDestination | None:
        model = await self._session.get(
            NotificationDestinationModel,
            destination_id,
        )

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all(
        self,
    ) -> list[NotificationDestination]:
        statement = select(NotificationDestinationModel).order_by(
            NotificationDestinationModel.created_at
        )

        result = await self._session.execute(statement)

        return [self._to_entity(model) for model in result.scalars().all()]

    async def update(
        self,
        destination: NotificationDestination,
    ) -> NotificationDestination | None:
        model = await self._session.get(
            NotificationDestinationModel,
            destination.id,
        )

        if model is None:
            return None

        model.name = destination.name
        model.destination_type = destination.destination_type
        model.enabled = destination.enabled
        model.webhook_url = destination.webhook_url
        model.webhook_secret = destination.webhook_secret

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(
        self,
        destination_id: UUID,
    ) -> bool:
        model = await self._session.get(
            NotificationDestinationModel,
            destination_id,
        )

        if model is None:
            return False

        await self._session.delete(model)

        await self._session.flush()

        return True

    @staticmethod
    def _to_entity(
        model: NotificationDestinationModel,
    ) -> NotificationDestination:
        return NotificationDestination(
            id=model.id,
            name=model.name,
            destination_type=model.destination_type,
            enabled=model.enabled,
            webhook_url=model.webhook_url,
            webhook_secret=model.webhook_secret,
            created_at=model.created_at,
        )
