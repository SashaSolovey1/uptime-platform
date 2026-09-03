from uuid import UUID

from uptime_platform.notifications.entities import (
    NotificationDestination,
)


class InMemoryNotificationDestinationRepository:
    def __init__(self) -> None:
        self._destinations: dict[
            UUID,
            NotificationDestination,
        ] = {}

    async def create(
        self,
        destination: NotificationDestination,
    ) -> NotificationDestination:
        self._destinations[destination.id] = destination

        return destination

    async def get_by_id(
        self,
        destination_id: UUID,
    ) -> NotificationDestination | None:
        return self._destinations.get(destination_id)

    async def get_all(
        self,
    ) -> list[NotificationDestination]:
        return list(self._destinations.values())

    async def update(
        self,
        destination: NotificationDestination,
    ) -> NotificationDestination | None:
        if destination.id not in self._destinations:
            return None

        self._destinations[destination.id] = destination

        return destination

    async def delete(
        self,
        destination_id: UUID,
    ) -> bool:
        if destination_id not in self._destinations:
            return False

        del self._destinations[destination_id]

        return True
