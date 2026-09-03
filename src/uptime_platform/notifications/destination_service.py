from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from uptime_platform.notifications.entities import (
    NotificationDestination,
)
from uptime_platform.notifications.repository_protocols import (
    NotificationDestinationRepositoryProtocol,
)
from uptime_platform.notifications.schemas import (
    NotificationDestinationCreate,
    NotificationDestinationUpdate,
)


class NotificationDestinationService:
    def __init__(
        self,
        repository: NotificationDestinationRepositoryProtocol,
    ) -> None:
        self._repository = repository

    async def create(
        self,
        data: NotificationDestinationCreate,
    ) -> NotificationDestination:
        destination = NotificationDestination(
            id=uuid4(),
            name=data.name,
            destination_type=data.destination_type,
            enabled=data.enabled,
            webhook_url=str(data.webhook_url),
            webhook_secret=data.webhook_secret,
            created_at=datetime.now(UTC),
        )

        return await self._repository.create(destination)

    async def get_all(
        self,
    ) -> list[NotificationDestination]:
        return await self._repository.get_all()

    async def get_by_id(
        self,
        destination_id: UUID,
    ) -> NotificationDestination | None:
        return await self._repository.get_by_id(destination_id)

    async def update(
        self,
        destination_id: UUID,
        data: NotificationDestinationUpdate,
    ) -> NotificationDestination | None:
        destination = await self._repository.get_by_id(destination_id)

        if destination is None:
            return None

        changes = data.model_dump(
            exclude_unset=True,
            mode="json",
        )

        updated_destination = replace(
            destination,
            **changes,
        )

        return await self._repository.update(updated_destination)

    async def delete(
        self,
        destination_id: UUID,
    ) -> bool:
        return await self._repository.delete(destination_id)
